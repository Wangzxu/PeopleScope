import chromadb
import uuid
from core.config import CHROMA_PERSIST_DIRECTORY


class ChromaHandler:
    """
    ChromaDB 数据库处理类，负责初始化客户端连接及 collection 管理。
    用于聊天记录的长期记忆存储。
    """

    def __init__(self, embedding_service):
        # 初始化 ChromaDB 持久化客户端
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIRECTORY)
        self.embedding_service = embedding_service
        # 获取或创建名为 'chat_memory' 的集合
        self.collection = self.client.get_or_create_collection("chat_memory")

    def get_collection(self):
        """获取聊天记忆集合"""
        return self.collection

    def get_client(self):
        """获取 ChromaDB 客户端"""
        return self.client

    def add_chat(self, user: str, content: str, metadata: dict):
        """
        添加聊天记录到 ChromaDB
        :param user: 用户名 (主要用于分区/过滤，虽metadata已有，但为了清晰)
        :param content: 聊天内容
        :param metadata: 其他元数据 (session_id, type, etc.)
        """
        # 生成唯一ID
        doc_id = str(uuid.uuid4())
        
        # 生成向量
        embedding = self.embedding_service.embed_query(content)
        
        # 确保 user 在 metadata 中
        if "user" not in metadata:
            metadata["user"] = user

        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )

    def query_similar_chats(self, user: str, query_text: str, n_results: int = 3):
        """
        查询最相关的聊天记录
        :param user: 用户名 (用于过滤)
        :param query_text: 查询文本
        :param n_results: 返回结果数量
        :return: 相关聊天记录列表 (content list)
        """
        query_embedding = self.embedding_service.embed_query(query_text)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"user": user} # 过滤当前用户
        )
        
        # results["documents"] 是 list of list
        if results["documents"] and len(results["documents"]) > 0:
            return results["documents"][0]
        return []

    def query_similar_facts(self, user: str, query_text: str, n_results: int = 3):
        """
        查询最相关的事实记忆
        :param user: 用户名 (用于过滤)
        :param query_text: 查询文本
        :param n_results: 返回结果数量
        :return: 相关事实列表 (content list)
        """
        query_embedding = self.embedding_service.embed_query(query_text)

        # 过滤条件：用户匹配 且 类型为事实(type=2)
        # ChromaDB where dict implies AND
        where_filter = {
            "$and": [
                {"user": {"$eq": user}},
                {"type": {"$eq": 2}}
            ]
        }

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )

        # results["documents"] 是 list of list
        if results["documents"] and len(results["documents"]) > 0:
            return results["documents"][0]
        return []

    def check_fact_exists(self, user: str, fact_text: str, threshold: float = 0.15) -> bool:
        """
        检查是否存在相似的事实
        :param user: 用户名
        :param fact_text: 待检查的事实文本
        :param threshold: 相似度阈值 (距离越小越相似，0为完全相同。默认0.15约为92.5%相似度)
        :return: True if exists, False otherwise
        """
        query_embedding = self.embedding_service.embed_query(fact_text)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=1,
            where={"user": user},
            include=["distances"]
        )
        
        if results["distances"] and len(results["distances"][0]) > 0:
            distance = results["distances"][0][0]
            if distance < threshold:
                return True
        return False

    def delete_chats_by_session(self, session_id: int):
        """
        根据会话ID删除相关聊天记录
        """
        try:
            self.collection.delete(
                where={"session_id": session_id}
            )
        except Exception as e:
            # 记录日志或忽略，视情况而定
            pass


