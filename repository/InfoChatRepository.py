from model.basicHardware import BasicHardware, FriendHardware
from model.chat import ChatModel
from core.db.mysql import MySQLHandler


class InfoChatRepository:
    def __init__(self, mysql: MySQLHandler, mogo: MySQLHandler):
        self.mysql = mysql
        self.mogo = mogo

    def get_by_user(self, user: str) -> BasicHardware:
        session = self.mysql.get_session()
        try:
            return session.query(BasicHardware).filter(BasicHardware.user == user).first()
        finally:
            session.close()

    def get_friend_by_user(self, user: str) -> FriendHardware:
        session = self.mysql.get_session()
        try:
            return session.query(FriendHardware).filter(FriendHardware.user == user).first()
        finally:
            session.close()

    def save_or_update_hardware(self, hardware: BasicHardware):
        session = self.mysql.get_session()
        try:
            existing = session.query(BasicHardware).filter(BasicHardware.user == hardware.user).first()
            if existing:
                existing.birth_year = hardware.birth_year
                existing.height = hardware.height
                existing.city = hardware.city
                existing.education = hardware.education
                existing.occupation = hardware.occupation
                existing.income_level = hardware.income_level
                existing.smoking_drinking = hardware.smoking_drinking
                existing.hometown = hardware.hometown
                session.commit()
                session.refresh(existing)
                return existing
            else:
                session.add(hardware)
                session.commit()
                session.refresh(hardware)
                return hardware
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def save_or_update_friend_hardware(self, hardware: FriendHardware):
        session = self.mysql.get_session()
        try:
            existing = session.query(FriendHardware).filter(FriendHardware.user == hardware.user).first()
            if existing:
                existing.birth_year_min = hardware.birth_year_min
                existing.birth_year_max = hardware.birth_year_max
                existing.height_min = hardware.height_min
                existing.height_max = hardware.height_max
                existing.city = hardware.city
                existing.education = hardware.education
                existing.occupation = hardware.occupation
                existing.income_level = hardware.income_level
                existing.smoking_drinking = hardware.smoking_drinking
                existing.hometown = hardware.hometown
                session.commit()
                session.refresh(existing)
                return existing
            else:
                session.add(hardware)
                session.commit()
                session.refresh(hardware)
                return hardware
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_chats_by_session(self, session_id):
        session = self.mysql.get_session()
        try:
            return (session.query(ChatModel)
                    .filter(ChatModel.session_id == session_id)
                    .order_by(ChatModel.msg_index)
                    .all())
        finally:
            session.close()

    def save_chat(self, chat: ChatModel):
        session = self.mysql.get_session()
        try:
            session.add(chat)
            session.commit()
            session.refresh(chat)
            return chat
        except:
            session.rollback()
            raise
        finally:
            session.close()
