from datetime import datetime
from sqlalchemy import func, asc

from db import db
from models.BaseModel import BaseModel
from utils.Enums import DebitCredit, Currency, ResponseCode

class TransactionModel(db.Model, BaseModel):
    __tablename__ = "transaction"

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime)

    message_id = db.Column(db.String(36))
    user_id = db.Column(db.String(36)) # usually a foreign key as a user should be a model
    amount = db.Column(db.Integer)
    currency = db.Column(db.Enum(Currency))
    debit_or_credit = db.Column(db.Enum(DebitCredit))
    response_code = db.Column(db.Enum(ResponseCode))
    
    def __init__(self, message_id, user_id, amount, currency, debit_or_credit, response_code):
        self.date_created = datetime.utcnow()
        self.message_id = message_id
        self.user_id = user_id
        self.amount = amount
        self.currency = currency
        self.debit_or_credit = debit_or_credit
        self.response_code = response_code

    @classmethod
    def get_all_for_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def get_all_accepted_for_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id, response_code=ResponseCode.APPROVED).all()

    @classmethod
    def get_all_for_message(cls, message_id):
        return cls.query.filter_by(message_id=message_id).all()
