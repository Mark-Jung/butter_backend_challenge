from utils.Logger import Logger
from utils.Enums import DebitCredit, Currency, ResponseCode

from cache import cache

from controllers.TransactionController import TransactionController

class TransactionManager:
    logger = Logger(__name__)

    """
    gets messageId, userId, and transactionAmount. 
    1. need to check transactionAmount
    2. create Transaction with TransactionController
    3. update the user's balance in cache.
    4. return userId, messageId, and balance
    """
    @classmethod
    def load_credit(cls, messageId, userId, transactionAmount):
        # 1. validates transactionAmount
        err, marshalled_transaction_amount, status = cls.marshall_transaction_amount(transactionAmount, DebitCredit.CREDIT)
        if err:
            return err, None, status
        
        # 2. creates transaction
        err, transaction, status = TransactionController.create_transaction(messageId, userId, marshalled_transaction_amount["amount"], marshalled_transaction_amount["currency"], marshalled_transaction_amount["debitOrCredit"])
        if err:
            return err, None, status
        
        # 3. updates balance in cache
        if cache.has(userId):
            balance = cache.get(userId)
        else:
            balance = 0
        balance += transaction.amount
        cache.set(userId, balance, timeout=3600) # balance is cached for 1 hour

        # return userId
        response = cls.package_transaction_response(userId, messageId, balance, transaction.currency.value, transaction.debit_or_credit.value)
        return None, response, status

    """
    gets messageId, userId, and transactionAmount. 
    1. need to check transactionAmount
    2. check if we have enough balance
    3. create Transaction with TransactionController
    4. update the user's balance in cache. (if necessary)
    5. return userId, messageId, responseCode and balance
    """
    @classmethod
    def authorize_debit(cls, messageId, userId, transactionAmount):
        err, marshalled_transaction_amount, status = cls.marshall_transaction_amount(transactionAmount, DebitCredit.DEBIT)
        if err:
            return err, None, status
        
        update_cache = False

        # get balance from cache or calculate
        if cache.has(userId):
            balance = cache.get(userId)
        else:
            balance = TransactionController.get_balance(userId)
            update_cache = True
        # determine response code from balance
        response_code = ResponseCode.DECLINED
        if balance > marshalled_transaction_amount["amount"]:
            response_code = ResponseCode.APPROVED
            balance -= marshalled_transaction_amount["amount"]
            update_cache = True

        err, transaction, status = TransactionController.create_transaction(messageId, userId, marshalled_transaction_amount["amount"], marshalled_transaction_amount["currency"], marshalled_transaction_amount["debitOrCredit"], response_code=response_code)
        if err:
            return err, None, status
        
        # update in cache
        if update_cache:
            cache.set(userId, balance, timeout=3600) # balance is cached for 1 hour

        response = cls.package_transaction_response(userId, messageId, balance, transaction.currency.value, transaction.debit_or_credit.value)
        response["responseCode"] = transaction.response_code.value 
        return None, response, status
    
    """
    marshalls transaction_amount
        if amount can be converted to float, is greater than 0
        if currency is one of what we support
        if debitOrCredit is either DEBIT or CREDIT and expected (load -> credit, authorize -> debit)
    """
    @classmethod
    def marshall_transaction_amount(cls, transaction_amount, expected_debit_or_credit): 
        amount = transaction_amount["amount"]
        try:
            amount_in_float = float(amount)
        except:
            cls.logger.exception("Failed to convert amount: " + amount)
            return "Ill-formed amount", None, 400
        if amount_in_float <= 0:
            return "Can only add non-zero positive balance", None, 400
        
        currency = transaction_amount["currency"]
        if not (Currency.in_values(currency)): 
            return "Not supported currency", None, 400
        else:
            currency = Currency[currency]
        
        debit_or_credit = transaction_amount["debitOrCredit"]
        if debit_or_credit != expected_debit_or_credit.value:
            return "Cannot be " + debit_or_credit, None, 400
        else:
            debit_or_credit = DebitCredit[debit_or_credit]

        multiplier = Currency.get_multiplier(currency)
        if multiplier == -1:
            cls.logger.exception("Multiplier for currency " + currency + " is not set.")
            return "Internal Server Error", None, 500

        multiplied_amount = amount_in_float * multiplier

        return "", {"amount": multiplied_amount, "currency": currency, "debitOrCredit": debit_or_credit}, 200

    @classmethod
    def package_transaction_response(cls, userId, messageId, balance, currency, debit_or_credit):
        balance_dict = {}
        balance_dict["amount"] = "{:.2f}".format(balance / float(100))
        balance_dict["currency"] = currency
        balance_dict["debitOrCredit"] = debit_or_credit
        response = {}
        response["userId"] = userId
        response["messageId"] = messageId
        response["balance"] = balance_dict
        return response
        

