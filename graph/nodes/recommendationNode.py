import json
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from graph.state.basicHardwareState import BasicHardwareState
from model.matchResult import MatchResult
from schema.matchResultSchema import RecommendationScore


class RecommendationNode:
    def __init__(self, match_repo, llm):
        self.match_repo = match_repo
        self.chat_model = llm
        self.structured_model = llm.with_structured_output(RecommendationScore)

    def __call__(self, state: BasicHardwareState):
        hardware_data = state["hardware_data"]
        friend_hardware_data = state["friend_hardware_data"]
    
        # 1. 检查是否需要重新进行硬过滤与打分（通过比对更新时间）
        needs_hard_filter = self.match_repo.check_needs_hard_filter(friend_hardware_data.user)
        
        if needs_hard_filter:
            # 2. 召回候选人 (在 MatchResultRepository.get_candidates 中已经只对年龄、身高进行了严格 SQL 过滤)
            candidates = self.match_repo.get_candidates(friend_hardware_data)
            
            if candidates:
                # 3. 为每个候选人打分并生成理由
                for candidate in candidates:
                    prompt = f"""
                    你是一个专业的红娘/推荐系统算法。你需要评估当前用户与一名候选人的匹配度。
                    【当前用户的条件】：
                    {hardware_data.model_dump(exclude_none=True)}
                    
                    【当前用户寻找的朋友（另一半）要求】:
                    {friend_hardware_data.model_dump(exclude_none=True)}
                    
                    【候选人实际信息】:
                    - 年龄/出生年份: {candidate.birth_year}
                    - 身高: {candidate.height}
                    - 城市: {candidate.city}
                    - 籍贯: {candidate.hometown}
                    - 学历: {candidate.education}
                    - 职业: {candidate.occupation}
                    - 收入: {candidate.income_level}
                    - 烟酒习惯: {candidate.smoking_drinking}
                    
                    请仔细对比用户的期望和候选人的实际情况。
                    给出一个 0 到 100 之间的匹配度分数，并生成一段不超过100字的推荐理由，向用户解释为什么匹配。
                    
                    【重要格式要求】：
                    你必须且只能返回包含以下两个字段的 JSON 结构：
                    - "score": 浮点数，代表匹配得分 (0-100)
                    - "match_reason": 字符串，代表推荐理由 (绝对不要使用 "reason" 或其他字段名)
                    """
                    
                    try:
                        # 调用大模型进行打分和评估
                        result: RecommendationScore = self.structured_model.invoke([SystemMessage(content="你是一个客观、精准的匹配评估引擎。"), HumanMessage(content=prompt)])
                        
                        if result.score > 0:
                            match_result = MatchResult(
                                source_user=friend_hardware_data.user,
                                target_user=candidate.user,
                                score=result.score,
                                match_reason=result.match_reason
                            )
                            self.match_repo.save_match_result(match_result)
                    except Exception as e:
                        print(f"Error scoring candidate {candidate.user}: {e}")

        # 4. 获取最新的推荐结果，并组装卡片数据
        detailed_matches = self.match_repo.get_matches_with_details(friend_hardware_data.user)
        
        if not detailed_matches:
            msg = "信息收集完毕！不过目前在我们的数据库中暂时没有找到特别符合你硬性要求的候选人，我们会持续为你关注！"
            return {"messages": [AIMessage(content=msg)]}

        # 取前 5 名最高分
        top_matches = detailed_matches[:5]
        
        # 提取第一个匹配者的关键信息用于生成有温度的话术
        best_match = top_matches[0]["hardware"]
        best_reason = top_matches[0]["match"].match_reason
        hometown_or_city = best_match.hometown or best_match.city or "未知地区"
        occupation_str = best_match.occupation or "未知职业"
        
        intro_prompt = f"""
        你是一个专业的金牌红娘。系统刚刚为用户匹配到了 {len(top_matches)} 位非常合适的候选人。
        请你用一段富有情感、惊喜的口吻（不要超过 50 字）向用户播报这个好消息。
        你可以提取第一位候选人的一个亮点（比如：来自{hometown_or_city}、或者职业是{occupation_str}）作为钩子吸引用户。
        示例："太棒了！根据你的要求，我为你精选了 {len(top_matches)} 位非常契合的伙伴。特别是第一位，和你一样也是来自新疆昌吉的后端开发哦！👇"
        
        第一位候选人亮点：
        - 匹配原因：{best_reason}
        - 城市/家乡：{hometown_or_city}
        - 职业：{occupation_str}
        """
        try:
            intro_res = self.chat_model.invoke([SystemMessage(content="你是一个热情的红娘助手。"), HumanMessage(content=intro_prompt)])
            intro_msg = intro_res.content
        except Exception as e:
            print(f"Error generating intro: {e}")
            intro_msg = f"太棒了！根据你的要求，我从库中为你精选了 {len(top_matches)} 位非常契合的伙伴。特别是第一位，{best_reason} 👇"

        # 构造卡片列表，利用 Markdown 的 code block 把结构化数据包裹起来
        # 前端收到后可通过正则提取 <cards>...</cards> 标签内的数据来渲染 Carousel 和抽屉详情。
        cards_data = []
        from datetime import datetime
        current_year = datetime.now().year
        
        for item in top_matches:
            hw = item["hardware"]
            match = item["match"]
            age = (current_year - hw.birth_year) if hw.birth_year else "未知"
            
            cards_data.append({
                "user_id": hw.user,
                "nickname": hw.user,  # 假设用user代替昵称
                "age": age,
                "height": hw.height,
                "city": hw.city,
                "hometown": hw.hometown,
                "occupation": hw.occupation,
                "education": hw.education,
                "income_level": hw.income_level,
                "smoking_drinking": hw.smoking_drinking,
                "score": match.score,
                "match_reason": match.match_reason
            })
            
        import json
        cards_json = json.dumps(cards_data, ensure_ascii=False)
        final_response = f"{intro_msg}\n\n<cards>{cards_json}</cards>"

        return {"messages": [AIMessage(content=final_response)]}
