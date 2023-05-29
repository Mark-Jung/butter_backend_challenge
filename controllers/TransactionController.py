from utils.Logger import Logger
from utils.Enums import DebitCredit, ResponseCode

from models.TransactionModel import TransactionModel

class TransactionController:
    logger = Logger(__name__)

    """
    1. create TransactionModel
    2. return TransactionModel object with 201
    """
    @classmethod
    def create_transaction(cls, message_id, user_id, amount, currency, debit_or_credit, response_code=ResponseCode.APPROVED):
        # what if there already is a transaction with the same mesage id? return 200 if the data match for idempotency?
        try:
            new_transaction = TransactionModel(message_id, user_id, amount, currency, debit_or_credit, response_code)
            new_transaction.save_to_db()
        except Exception as ex:
            cls.logger.exception("Error while creating transaction: " + ex)
            return "Internal Server Error", None, 500

        return "", new_transaction, 201
    
    """
    1. get all accepted transactions
    2. return TransactionModel object with 201
    """
    @classmethod
    def get_balance(cls, user_id):
        all_accepted_transactions_for_user = TransactionModel.get_all_accepted_for_user(user_id)
        total = 0
        for transaction in all_accepted_transactions_for_user:
            amount = transaction.amount
            if (transaction.debit_or_credit == DebitCredit.DEBIT):
                amount *= -1
            total += amount
        return total