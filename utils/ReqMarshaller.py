class ReqMarshaller:
    @classmethod
    def check_body(cls, req, params):
        for param in params:
            if param[0] not in req or not isinstance(req[param[0]], param[1]):
                return False
        return True
