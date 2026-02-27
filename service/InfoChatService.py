from langchain_core.messages import HumanMessage, AIMessage
from core.logger import get_logger
from model.chat import ChatModel
from model.basicHardware import BasicHardware, FriendHardware
from schema.hardwareSchema import BasicHardwareSchema, FriendHardwareSchema
from graph.state.basicHardwareState import BasicHardwareState
from repository.InfoChatRepository import InfoChatRepository

logger = get_logger(__name__)


class InfoChatService:
    def __init__(self, info_repo: InfoChatRepository, info_graph):
        self.info_repo = info_repo
        self.info_graph = info_graph

    def generate_chat(self, user: str, session_id: int, message: str):
        # 1. 获取硬件信息
        hardware_model = self.info_repo.get_by_user(user)
        friend_hardware_model = self.info_repo.get_friend_by_user(user)

        # 转换为 Schema
        if hardware_model:
            hardware_data = BasicHardwareSchema(
                user=hardware_model.user,
                birth_year=hardware_model.birth_year,
                height=hardware_model.height,
                city=hardware_model.city,
                education=hardware_model.education,
                occupation=hardware_model.occupation,
                income_level=hardware_model.income_level,
                smoking_drinking=hardware_model.smoking_drinking,
                hometown=hardware_model.hometown
            )
        else:
            hardware_data = BasicHardwareSchema(user=user)

        if friend_hardware_model:
            friend_hardware_data = FriendHardwareSchema(
                user=friend_hardware_model.user,
                birth_year=friend_hardware_model.birth_year,
                height=friend_hardware_model.height,
                city=friend_hardware_model.city,
                education=friend_hardware_model.education,
                occupation=friend_hardware_model.occupation,
                income_level=friend_hardware_model.income_level,
                smoking_drinking=friend_hardware_model.smoking_drinking,
                hometown=friend_hardware_model.hometown
            )
        else:
            friend_hardware_data = FriendHardwareSchema(user=user)

        # 2. 获取聊天历史并构建 State
        history_models = self.info_repo.get_chats_by_session(session_id)
        
        messages = []
        for chat in history_models:
            if chat.type == 0:  # User
                messages.append(HumanMessage(content=chat.content))
            elif chat.type == 1:  # AI
                messages.append(AIMessage(content=chat.content))

        # 添加当前用户消息
        messages.append(HumanMessage(content=message))

        # 构造 State (初始只需提供数据，missing_fields 由节点计算)
        state: BasicHardwareState = {
            "hardware_data": hardware_data,
            "friend_hardware_data": friend_hardware_data,
            "messages": messages,
            "missing_fields": [],
            "friend_missing_fields": [],
            "is_complete": False,
            "friend_is_complete": False
        }

        # 3. 调用 Graph
        result = self.info_graph.invoke(state)

        # 4. 更新硬件信息
        updated_data = result["hardware_data"]
        updated_friend_data = result["friend_hardware_data"]
        
        # 将 Schema 转回 Model 并保存
        new_hardware = BasicHardware(
            user=user,
            birth_year=updated_data.birth_year,
            height=updated_data.height,
            city=updated_data.city,
            education=updated_data.education,
            occupation=updated_data.occupation,
            income_level=updated_data.income_level,
            smoking_drinking=updated_data.smoking_drinking,
            hometown=updated_data.hometown
        )
        self.info_repo.save_or_update_hardware(new_hardware)

        new_friend_hardware = FriendHardware(
            user=user,
            birth_year=updated_friend_data.birth_year,
            height=updated_friend_data.height,
            city=updated_friend_data.city,
            education=updated_friend_data.education,
            occupation=updated_friend_data.occupation,
            income_level=updated_friend_data.income_level,
            smoking_drinking=updated_friend_data.smoking_drinking,
            hometown=updated_friend_data.hometown
        )
        self.info_repo.save_or_update_friend_hardware(new_friend_hardware)

        # 获取 AI 回复
        # 如果图执行结束，最后的消息应该是 AI 的追问
        if result["messages"] and result["messages"][-1].type == 'ai':
            ai_response_content = result["messages"][-1].content
        else:
            # 如果没有 AI 回复 (比如已经 complete 了，或者中间状态)，给个默认或者结束语
            if result.get("friend_is_complete"):
                ai_response_content = "感谢配合，您和您期望找的朋友的信息都已收集完毕。"
            else:
                ai_response_content = "..." # Should not happen ideally if graph is correct

        return ai_response_content

    def save_chat(self, session_id: int, type: int, content: str):
        chats = self.info_repo.get_chats_by_session(session_id)
        if len(chats) > 0:
            msg_index = chats[-1].msg_index + 1
        else:
            msg_index = 0
            
        chat = ChatModel(session_id=session_id, type=type, content=content, msg_index=msg_index)
        self.info_repo.save_chat(chat)



