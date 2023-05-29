import os, sys
import unittest
from unittest.mock import MagicMock
import json
import copy

from cache import cache

from models.TransactionModel import TransactionModel
from controllers.TransactionController import TransactionController
from utils.Enums import Currency

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
basedir = os.path.abspath(os.path.dirname(__file__))

from app import app
from db import db

TEST_DB = 'test.db'

class CreditLoadTests(unittest.TestCase):
    valid_credit_load_request = {
        "messageId": "123message",
        "userId": "123message", 
        "transactionAmount": {
            "amount": "123.50",
            "currency": "USD",
            "debitOrCredit": "CREDIT",
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
    
    def test_Given_blank_When_valid_credit_load_sent_Then_create_transaction_and_update_cache(self):
        """
        Setup: None
        When:
            1. valid credit load request is sent
        Then:
            1. create a transaction and return with 201
            2. update cache
        """
        valid_credit_load_request = copy.deepcopy(self.valid_credit_load_request)
        self.assertFalse(cache.has(valid_credit_load_request["userId"]))
        credit_load_response = self.app.put("/load/"+valid_credit_load_request["messageId"], data=json.dumps(valid_credit_load_request))
        self.assertEqual(201, credit_load_response.status_code)
        response_data = json.loads(credit_load_response.data)
        self.assertEqual(valid_credit_load_request["messageId"], response_data["messageId"])
        self.assertEqual(valid_credit_load_request["userId"], response_data["userId"])
        self.assertEqual(valid_credit_load_request["transactionAmount"]["amount"], response_data["balance"]["amount"])
        self.assertEqual(valid_credit_load_request["transactionAmount"]["currency"], response_data["balance"]["currency"])
        self.assertEqual(valid_credit_load_request["transactionAmount"]["debitOrCredit"], response_data["balance"]["debitOrCredit"])
        self.assertTrue(cache.has(valid_credit_load_request["userId"]))
        self.assertEqual(float(valid_credit_load_request["transactionAmount"]["amount"]) * Currency.get_multiplier(Currency.USD), cache.get(valid_credit_load_request["userId"]))

        valid_credit_load_request["messageId"] = valid_credit_load_request["messageId"] + "onemore"
        credit_load_response = self.app.put("/load/"+valid_credit_load_request["messageId"], data=json.dumps(valid_credit_load_request))
        self.assertEqual(201, credit_load_response.status_code)
        self.assertTrue(cache.has(valid_credit_load_request["userId"]))
        response_data = json.loads(credit_load_response.data)
        self.assertEqual(float(response_data["balance"]["amount"]) * Currency.get_multiplier(Currency.USD), cache.get(valid_credit_load_request["userId"]))

    def test_Given_blank_When_credit_load_with_invalid_amount_sent_Then_400(self):
        """
        Setup: None
        When:
            1. invalid credit load request is sent. (negative or 0, non-float like text string)
        Then:
            1. Dont' create transaction and return with 400
        """
        # negative
        invalid_amount_credit_load_request = copy.deepcopy(self.valid_credit_load_request.copy())
        invalid_amount_credit_load_request["transactionAmount"]["amount"] = "-100.50"
        credit_load_response = self.app.put("/load/"+invalid_amount_credit_load_request["messageId"], data=json.dumps(invalid_amount_credit_load_request))
        self.assertEqual(400, credit_load_response.status_code)

        # zero
        invalid_amount_credit_load_request["transactionAmount"]["amount"] = "0"
        credit_load_response = self.app.put("/load/"+invalid_amount_credit_load_request["messageId"], data=json.dumps(invalid_amount_credit_load_request))
        self.assertEqual(400, credit_load_response.status_code)

        # empty string
        invalid_amount_credit_load_request["transactionAmount"]["amount"] = ""
        credit_load_response = self.app.put("/load/"+invalid_amount_credit_load_request["messageId"], data=json.dumps(invalid_amount_credit_load_request))
        self.assertEqual(400, credit_load_response.status_code)

    def test_Given_blank_When_credit_load_with_invalid_currency_sent_Then_400(self):
        """
        Setup: None
        When:
            1. invalid credit load request is sent. (currency that is not supported)
        Then:
            1. Dont' create transaction and return with 400
        """
        # non usd
        invalid_currency_credit_load_request = copy.deepcopy(self.valid_credit_load_request)
        invalid_currency_credit_load_request["transactionAmount"]["currency"] = "WON"
        credit_load_response = self.app.put("/load/"+invalid_currency_credit_load_request["messageId"], data=json.dumps(invalid_currency_credit_load_request))
        self.assertEqual(400, credit_load_response.status_code)

        # empty string
        invalid_currency_credit_load_request["transactionAmount"]["currency"] = ""
        credit_load_response = self.app.put("/load/"+invalid_currency_credit_load_request["messageId"], data=json.dumps(invalid_currency_credit_load_request))
        self.assertEqual(400, credit_load_response.status_code)



