from pymongo import MongoClient
from core.config import MONGO_URI, MONGO_DB_NAME
from datetime import datetime

class MongoDatabase:
    """
    MongoDB database implementation class.
    Initializes connection using environment variables loaded in core.config.
    """
    _instance = None
    _client = None
    _db = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MongoDatabase, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._client = MongoClient(MONGO_URI)
            self._db = self._client[MONGO_DB_NAME]

    @property
    def db(self):
        return self._db

    @property
    def client(self):
        return self._client

        def get_collection(self, collection_name):

            return self._db[collection_name]

    

        def save_user_tags(self, user: str, tags: dict):

            """

            Save or update user tags.

            :param user: Username or User ID

            :param tags: Dictionary of tags e.g. {"hobbies": ["reading"], "personality": ["introvert"]}

            """

            collection = self.get_collection("user_tags")

            collection.update_one(

                {"user": user},

                {"$set": {"tags": tags, "updated_at": datetime.utcnow()}},

                upsert=True

            )

    

        def save_chat(self, session_id: int, message_type: int, content: str, user: str = None):

            """

            Save a chat message.

            :param session_id: ID of the chat session

            :param message_type: 0 for user, 1 for AI (following SQL schema convention)

            :param content: The message content

            :param user: Optional username associated with the chat

            """

            collection = self.get_collection("chats")

            chat_doc = {

                "session_id": session_id,

                "type": message_type,

                "content": content,

                "created_at": datetime.utcnow()

            }

            if user:

                chat_doc["user"] = user

                

            collection.insert_one(chat_doc)

    

        def save_aggregation(self, user: str, aggregation_data: dict):

            """

            Save or update user aggregation data.

            :param user: Username

            :param aggregation_data: Dictionary containing aggregation fields (summary, traits, etc.)

            """

            collection = self.get_collection("aggregations")

            # Ensure we don't overwrite with empty data if we want to merge, 

            # but usually aggregation is a snapshot. We'll verify what keys are present.

            

            update_data = aggregation_data.copy()

            update_data["updated_at"] = datetime.utcnow()

            

            collection.update_one(

                {"user": user},

                {"$set": update_data},

                upsert=True

            )

    

    # Create a global instance

    mongo_db = MongoDatabase()


def get_mongo_db():
    """
    Dependency to get the MongoDB database instance.
    """
    return mongo_db.db
