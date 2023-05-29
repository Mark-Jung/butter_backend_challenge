import enum

class ExtendedEnum(enum.Enum):
    @classmethod
    def in_values(cls, value):
        return value in list(map(lambda c: c.value, cls))

"""
Debit or Credit flag for the network transaction. 
A Debit deducts funds from a user. A credit adds funds to a user.
"""
class DebitCredit(ExtendedEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

"""
The response code sent back to the network for the merchant. Multiple declines
reasons may exist but only one will be sent back to the network. Advice messages
will include the response code that was sent on our behalf.
"""
class ResponseCode(ExtendedEnum):
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"

"""
List of supported currencies
"""
class Currency(ExtendedEnum):
    USD = "USD"

    @classmethod
    def get_multiplier(cls, currency):
        if (currency == cls.USD):
            return 100
        return -1
