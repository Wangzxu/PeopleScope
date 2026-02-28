import json
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from graph.state.basicHardwareState import BasicHardwareState
from core.model import LLMFactory
from model.matchResult import MatchResult
from schema.matchResultSchema import RecommendationScore


def recommendation_node(state: BasicHardwareState):
    from core.container import db_container
    
    hardware_data = state["hardware_data"]
    friend_hardware_data = state["friend_hardware_data"]

    # 获取 Repository
    match_repo = db_container.match_result_repo

    # 1. 检查是否需要重新进行硬过滤与打分（通过比对更新时间）
    needs_hard_filter = match_repo.check_needs_hard_filter(friend_hardware_data.user)

    if not needs_hard_filter:
        # 直接使用现有匹配结果，跳过大模型重新打分
        existing_matches = match_repo.get_existing_matches(friend_hardware_data.user)
        if existing_matches:
            msg = f"感谢配合！✨\n根据你现有的期望条件（无新变动），系统已经为你保留了 {len(existing_matches)} 位高匹配度的潜在人选！我们会稍后为你展示详细推荐。"
        else:
            msg = "感谢配合！你的要求没有改变，目前数据库里暂时还是没有特别符合你要求的人选，我们会持续为你关注！"
        return {"messages": [AIMessage(content=msg)]}

    # 2. 召回候选人 (在 MatchResultRepository.get_candidates 中已经只对年龄、身高进行了严格 SQL 过滤)
    candidates = match_repo.get_candidates(friend_hardware_data)

    if not candidates:
        return {"messages": [AIMessage(content="信息收集完毕！不过目前在我们的数据库中暂时没有找到符合你年龄/身高硬性要求的候选人，我们会持续为你关注！")]}

    llm = LLMFactory.get_model().with_structured_output(RecommendationScore)

    # 2. 为每个候选人打分并生成理由
    successful_matches = 0
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
            result: RecommendationScore = llm.invoke([SystemMessage(content="你是一个客观、精准的匹配评估引擎。"), HumanMessage(content=prompt)])
            
            # 只保存分数达到一定阈值的推荐 (例如 > 60分)，或者保存所有
            if result.score > 0:
                match_result = MatchResult(
                    source_user=friend_hardware_data.user,
                    target_user=candidate.user,
                    score=result.score,
                    match_reason=result.match_reason
                )
                match_repo.save_match_result(match_result)
                successful_matches += 1
        except Exception as e:
            # 记录错误，继续处理下一个
            print(f"Error scoring candidate {candidate.user}: {e}")

    # 3. 生成最终回复
    msg = f"感谢你的耐心配合！你的所有信息都已记录完毕。✨\n"
    if successful_matches > 0:
        msg += f"基于你的期望，系统已经为你匹配到了 {successful_matches} 位潜在的合适人选！我们会稍后为你展示详细推荐。"
    else:
        msg += "目前暂时没有特别高匹配度的人选，但我们的数据库在不断更新，有合适的人选会第一时间通知你！"

    return {"messages": [AIMessage(content=msg)]}
