from sqlalchemy.orm import Session
from model.aggregation import AggregationModel


class AggregationRepository:

    @staticmethod
    def create(db: Session, entity: AggregationModel):
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def update(db: Session, entity: AggregationModel):
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def get_by_id(db: Session, entity_id: int):
        entity = db.get_one(AggregationModel, entity_id)
        return entity

    @staticmethod
    def get_by_user(db: Session, user: str):
        return db.query(AggregationModel).filter(AggregationModel.user == user).first()


