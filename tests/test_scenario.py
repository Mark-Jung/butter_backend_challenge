import os, sys
import unittest
import json
import copy
from freezegun import freeze_time
import datetime

from cache import cache

from utils.Enums import Currency

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
basedir = os.path.abspath(os.path.dirname(__file__))

from app import app
from db import db

TEST_DB = 'test.db'

class TransactionScenarioTests(unittest.TestCase):
    valid_debit_authorization_request = {
        "messageId": "123debitmessage",
        "userId": "123message", 
        "transactionAmount": {
            "amount": "123.50",
            "currency": "USD",
            "debitOrCredit": "DEBIT",
        }
    }

    valid_credit_load_request = {
        "messageId": "123creditmessage",
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
    
    def test_Given_sufficient_credit_When_valid_debit_authorization_sent_Then_create_transaction_and_deduct_from_balance(self):
        """
        Setup:
            1. send valid credit load to build up sufficient balance.
        When:
            1. valid debit authorization request is sent
        Then:
            1. create a transaction and return with 201.
            2. update balance in cache
                2.a cache also expires after 1 hour
        """
        initial_datetime = datetime.datetime.now()
        with freeze_time(initial_datetime) as frozen_datetime:
            valid_credit_load_request = copy.deepcopy(self.valid_credit_load_request)
            self.assertFalse(cache.has(valid_credit_load_request["userId"]))
            n = 5
            # credit should be valid_credit_load_request["transactionAmount"]["amount"] * 5
            for i in range(n):
                credit_load_response = self.app.put("/load/"+valid_credit_load_request["messageId"], data=json.dumps(valid_credit_load_request))
                self.assertEqual(201, credit_load_response.status_code)
            
            self.assertTrue(cache.has(valid_credit_load_request["userId"]))
            valid_debit_authorization_request = copy.deepcopy(self.valid_debit_authorization_request)
            debit_authorization_response = self.app.put("/authorization/"+valid_debit_authorization_request["messageId"], data=json.dumps(valid_debit_authorization_request))
            self.assertEqual(201, debit_authorization_response.status_code)
            expected_balance = (float(valid_credit_load_request["transactionAmount"]["amount"]) * n - float(valid_debit_authorization_request["transactionAmount"]["amount"]))
            self.assertEqual(Currency.get_multiplier(Currency.USD) * expected_balance, cache.get(valid_credit_load_request["userId"]))
            response_data = json.loads(debit_authorization_response.data)
            self.assertEqual(expected_balance, float(response_data["balance"]["amount"]))

            cache.clear()

            debit_authorization_response = self.app.put("/authorization/"+valid_debit_authorization_request["messageId"], data=json.dumps(valid_debit_authorization_request))
            self.assertEqual(201, debit_authorization_response.status_code)
            expected_balance = (float(valid_credit_load_request["transactionAmount"]["amount"]) * n - float(valid_debit_authorization_request["transactionAmount"]["amount"]) * 2)
            self.assertEqual(Currency.get_multiplier(Currency.USD) * expected_balance, cache.get(valid_credit_load_request["userId"]))
            response_data = json.loads(debit_authorization_response.data)
            self.assertEqual(expected_balance, float(response_data["balance"]["amount"]))

            frozen_datetime.tick(delta=datetime.timedelta(seconds=3601))
            self.assertFalse(cache.has(valid_credit_load_request["userId"]))
        

