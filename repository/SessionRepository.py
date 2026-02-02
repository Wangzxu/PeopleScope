from sqlalchemy.orm import Session
from model.session import SessionModel


class SessionRepository:
    @staticmethod
    def get_session_by_user(db:Session, user: str):
        return db.query(SessionModel).filter(SessionModel.user == user).all()

    @staticmethod
    def get_session_by_id(db: Session, session_id: int):
        return db.query(SessionModel).filter(SessionModel.id == session_id).first()

    @staticmethod
    def create_session(db: Session, user: str, title: str, content: str):
        session = SessionModel(user=user, title=title, content=content)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def update_session_title(db: Session, session_id: int, title: str):
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            session.title = title
            db.commit()
            db.refresh(session)
        return session

    @staticmethod
    def delete_session(db: Session, session_id: int):
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
