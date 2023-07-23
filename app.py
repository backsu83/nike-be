from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource, reqparse

from models import db, OrderModel

from routers.manager import Admin, login_manager, bcrypt
from routers.front import Front

import os

import datetime

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:figrontline!0704@34.64.207.81:5432/nike_by_hongdae"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:figrontline!0704@15.164.9.111:5432/nike_by_hongdae"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# flask-auth environment variables
app.config['SECRET_KEY'] = 'Nikey#Shoe!eeFindr@1235'
app.config['BCRYPT_LEVEL'] = 10

cors = CORS(app, resources={
    # r"/admin/*": {"origins": "http://192.168.50.15:3000"},
    r"/admin/*": {"origins": "*"},
    # "login": {"origins": ["35.216.111.100", "192.168.50.15:3000"]},
    "*": {"origins": '*'}
}, supports_credentials=True)
# cors = CORS(app, supports_credentials=True, origins="*")

app.config['SQLALCHEMY_POOL_SIZE'] = 20

api = Api(app, doc='/docs')
db.init_app(app)
login_manager.init_app(app)
bcrypt.init_app(app)
cors.init_app(app)

if 'PUBSUB_TOPIC' in os.environ:
    app.config['PUBSUB_TOPIC'] = os.environ['PUBSUB_TOPIC']
if 'PUBSUB_TOPIC' in os.environ:
    app.config['PUBSUB_VERIFICATION_TOKEN'] = os.environ['PUBSUB_VERIFICATION_TOKEN']


@api.route('/alive')
class HelloWorld(Resource):
    def get(self):
        return {"hello": "world!"}, 201, {"hi": "hello"}


@api.route('/deidentify')
class PubSubHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=dict, help="메시지 객체")
        parser.add_argument('key', type=str, help="메시지 객체")
        order_id = parser.parse_args()["id"]
        token = parser.parse_args()["key"]
        print(token)
        if token != app.config['PUBSUB_VERIFICATION_TOKEN']:
            return 403
        order = OrderModel.query.get(order_id)

        order.name = ""
        order.phone = '010-****-'+order.phone.split('-')[-1]
        db.session.merge(order)
        db.session.commit()

        return 200


api.add_namespace(Front, '/')
api.add_namespace(Admin, '/admin/')
