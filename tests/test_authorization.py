import os, sys
import unittest
import json
import copy

from cache import cache

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
basedir = os.path.abspath(os.path.dirname(__file__))

from app import app
from db import db

TEST_DB = 'test.db'

class DebitAuthorizationTests(unittest.TestCase):
    valid_debit_authorization_request = {
        "messageId": "123message",
        "userId": "123message", 
        "transactionAmount": {
            "amount": "123.50",
            "currency": "USD",
            "debitOrCredit": "DEBIT",
        }
    }

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        cls.app = app.test_client()
        cache.init_app(app)
        try:
            db.init_app(app)
        except:
            pass

    def setUp(self):
        cache.clear()
        with app.app_context():
            db.drop_all()
            db.create_all()
    
    def test_Given_insufficient_credit_When_valid_debit_authorization_sent_Then_create_transaction_and_update_cache(self):
        """
        Setup: None
        When:
            1. valid debit authorization request is sent
        Then:
            1. create a transaction and return with 201.
                1.a transaction should be declined
            2. update cache (to 0)
        """
        valid_debit_authorization_request = copy.deepcopy(self.valid_debit_authorization_request)
        self.assertFalse(cache.has(valid_debit_authorization_request["userId"]))
        debit_authorization_response = self.app.put("/authorization/"+valid_debit_authorization_request["messageId"], data=json.dumps(valid_debit_authorization_request))
        self.assertEqual(201, debit_authorization_response.status_code)
        response_data = json.loads(debit_authorization_response.data)
        self.assertEqual(valid_debit_authorization_request["messageId"], response_data["messageId"])
        self.assertEqual(valid_debit_authorization_request["userId"], response_data["userId"])
        self.assertNotEqual(valid_debit_authorization_request["transactionAmount"]["amount"], response_data["balance"]["amount"])
        self.assertEqual(0, float(response_data["balance"]["amount"]))
        self.assertEqual(valid_debit_authorization_request["transactionAmount"]["currency"], response_data["balance"]["currency"])
        self.assertEqual(valid_debit_authorization_request["transactionAmount"]["debitOrCredit"], response_data["balance"]["debitOrCredit"])
        self.assertTrue(cache.has(valid_debit_authorization_request["userId"]))
        self.assertEqual(0, cache.get(valid_debit_authorization_request["userId"]))

    def test_Given_blank_When_debit_authorization_with_invalid_amount_sent_Then_400(self):
        """
        Setup: None
        When:
            1. invalid debit authorization request is sent. (negative or 0, non-float like text string)
        Then:
            1. Dont' create transaction and return with 400
        """
        # negative
        invalid_amount_debit_authorization_request = copy.deepcopy(self.valid_debit_authorization_request.copy())
        invalid_amount_debit_authorization_request["transactionAmount"]["amount"] = "-100.50"
        debit_authorization_response = self.app.put("/load/"+invalid_amount_debit_authorization_request["messageId"], data=json.dumps(invalid_amount_debit_authorization_request))
        self.assertEqual(400, debit_authorization_response.status_code)

        # zero
        invalid_amount_debit_authorization_request["transactionAmount"]["amount"] = "0"
        debit_authorization_response = self.app.put("/load/"+invalid_amount_debit_authorization_request["messageId"], data=json.dumps(invalid_amount_debit_authorization_request))
        self.assertEqual(400, debit_authorization_response.status_code)

        # empty string
        invalid_amount_debit_authorization_request["transactionAmount"]["amount"] = ""
        debit_authorization_response = self.app.put("/load/"+invalid_amount_debit_authorization_request["messageId"], data=json.dumps(invalid_amount_debit_authorization_request))
        self.assertEqual(400, debit_authorization_response.status_code)

    def test_Given_blank_When_debit_authorization_with_invalid_currency_sent_Then_400(self):
        """
        Setup: None
        When:
            1. invalid debit authorization request is sent. (currency that is not supported)
        Then:
            1. Dont' create transaction and return with 400
        """
        # non usd
        invalid_currency_debit_authorization_request = copy.deepcopy(self.valid_debit_authorization_request)
        invalid_currency_debit_authorization_request["transactionAmount"]["currency"] = "WON"
        debit_authorization_response = self.app.put("/load/"+invalid_currency_debit_authorization_request["messageId"], data=json.dumps(invalid_currency_debit_authorization_request))
        self.assertEqual(400, debit_authorization_response.status_code)

        # empty string
        invalid_currency_debit_authorization_request["transactionAmount"]["currency"] = ""
        debit_authorization_response = self.app.put("/load/"+invalid_currency_debit_authorization_request["messageId"], data=json.dumps(invalid_currency_debit_authorization_request))
        self.assertEqual(400, debit_authorization_response.status_code)



