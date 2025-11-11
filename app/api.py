from flask import Flask, request
from flask_restful import Resource, Api
from database import db
import config

app = Flask(__name__)
api = Api(app)

def transform_cp(cp):
    return {
        "id": cp[0],
        "location": {
            "x": cp[1],
            "y": cp[2]
        },
        "name": cp[3],
        "price": cp[4],
        "state": cp[5],
        "pairing_info": {
            "paired": cp[6],
            "total_charged": cp[7]
        }
    }

class AllChargingPoints(Resource):
    def get(self):
        result = []
        try:
            cps = db.get_cps()
            for cp in cps:
                result.append(transform_cp(cp))
        except:
            pass
        return {"collection": result}

class ChargingPoint(Resource):
    def get(self, n):
        result = None
        if db.exists(n):
            cp = db.get_cp(n)
            result = transform_cp(cp)
        return result
    def put(self, n):
        json_data = request.get_json(force=True)
        state = json_data.get("state")
        print(state)
        if not db.exists(n):
            return {"message": "Charging point not found"}, 404

        if state is None:
            return {"message": "State is required"}, 400

        try:
            db.set_state(n, state)
            cp = db.get_cp(n)
            return transform_cp(cp), 200
        except Exception as e:
            return {"message": "Failed to update the charging point"}, 500

class Request(Resource):
    def get(self):
        return {"data": [["Justo ahora", "driver002", "CP001"]]}

class Log(Resource):
    def get(self):
        limit = request.args.get("limit", default=30, type=int)
        if config.LOG_FILE:
            config.LOG_FILE.seek(0)
            lines =  config.LOG_FILE.read().split('\n')
            data = lines[len(lines) - limit:]
            message = ""
            for line in data:
                message += line + "\n"
            return {"message": message}
        return {"message": ""}

class Weather(Resource):
    def get(self):
        return {"status": "OK"}

api.add_resource(ChargingPoint, "/cp/<string:n>")
api.add_resource(AllChargingPoints, "/cp/all")
api.add_resource(Request, "/requests")
api.add_resource(Log, "/log")
api.add_resource(Weather, "/weather")

def run_api():
    app.run(port=9999)
