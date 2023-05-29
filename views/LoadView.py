import json
from flask import request
from flask.views import MethodView

from utils.ReqMarshaller import ReqMarshaller
from utils.ResponseBuilder import ResponseBuilder

from managers.TransactionManager import TransactionManager


class LoadView(MethodView):

    @classmethod
    def load_credit(cls, messageId):
        try:
            data = json.loads(request.data)
        except Exception as ex:
            return ResponseBuilder.build("ill-formed request: " + ex, None, 400)

        req_params = [("userId", str), ("transactionAmount", dict)]
        if not ReqMarshaller.check_body(data, req_params):
            return ResponseBuilder.build("ill-formed request", None, 400)
        transactionAmount = data["transactionAmount"]
        req_params_for_transactionAmount = [("amount", str), ("currency", str), ("debitOrCredit", str)]
        if not ReqMarshaller.check_body(transactionAmount, req_params_for_transactionAmount):
            return ResponseBuilder.build("ill-formed request", None, 400)
        
        # messageId is from url, 
        # user_id, amount, currency, debitOrCredit is from request data
        err, response, status = TransactionManager.load_credit(messageId, data["userId"], transactionAmount)
        return ResponseBuilder.build(err, response, status)
