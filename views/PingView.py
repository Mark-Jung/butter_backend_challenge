from flask.views import MethodView
import json
import datetime

class PingView(MethodView):
    @classmethod
    def ping(cls):
        status = 200
        try:
            response = { "serverTime": str(datetime.datetime.now()) }
        except Exception as ex:
            response = { "message": "Unable to get server time: " + ex }
            status = 500

        return json.dumps(response), status
