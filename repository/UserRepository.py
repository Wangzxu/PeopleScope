from sqlalchemy.orm import Session

from model.user import UserModel


class UserRepository:
    @staticmethod
    def get_user_by_name(db: Session, user: str) -> UserModel:
        return db.query(UserModel).filter(UserModel.user == user).first()

    @staticmethod
    def update_user(db: Session, user: UserModel):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
