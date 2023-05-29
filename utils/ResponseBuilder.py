import json

class ResponseBuilder:

    @classmethod
    def build(cls, message, response, status):
        if message:
            return json.dumps({"message": message, "code": status}), status
        return json.dumps(response), status
