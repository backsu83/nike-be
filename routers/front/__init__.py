import os

from flask import request
from google.protobuf import timestamp_pb2
import datetime
import json

import requests
from flask_restx import Resource, marshal_with, reqparse
from google.cloud import storage
#from google.cloud import tasks_v2
from werkzeug.datastructures import FileStorage
import datetime
from google.cloud import storage
from werkzeug.utils import secure_filename

from models import db, AssetModel, ProductModel, OrderModel, OrderAssetMap, OptionModel
from routers.fields import Front, front_order_field, admin_asset_field, front_asset_field, \
    front_product_list_field, front_asset_list_field

send_url = 'https://apis.aligo.in/send/'

sms_data = {'key': '6j0abcafoim4l1mgtf0fpbuvbp1r1hyb',  # api key
            'userid': 'redmussa',  # 알리고 사이트 아이디
            'sender': '02-333-2094',  # 발신번호
            #'msg': 'NIKE BY YOU\n나이키 스타일 홍대\n%고객명%님 커스텀을 성공적으로 주문했습니다.\n직원에게 문의하여 결제를 진행해 주세요.',  # 문자 내용
            'msg': 'NIKE BY YOU\n나이키 스타일 홍대\n커스텀을 성공적으로 주문했습니다.\n직원에게 문의하여 결제를 진행해 주세요.',  # 문자 내용
            'msg_type': 'LMS',  # 메세지 타입 (SMS, LMS)
            'title': 'NIKE DO IT YOURSELF <홍대점>',  # 메세지 제목 (장문에 적용)
            # 'rdate' : '예약날짜',
            # 'rtime' : '예약시간',
            # 'testmode_yn' : '' #테스트모드 적용 여부 Y/N
            }


@Front.route('asset')
class AssetResponse(Resource):
    # @Quiz.expect(selection_field)
    @Front.response(200, 'Success', front_asset_list_field)
    @marshal_with(front_asset_list_field)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('custom_id', type=str, help="관리자 암호", location='args')
        custom_id = parser.parse_args()["custom_id"]
        parser.add_argument('option_id', type=str, help="관리자 암호", location='args')
        option_id = parser.parse_args()["option_id"]
        if custom_id is not None:
            asset = AssetModel.query.filter_by(custom_id=custom_id).all()
            return {"asset_list": asset}

        if option_id is not None:
            option = OptionModel.query.get(option_id)
            if option is None:
                return {"result": False}, 404
            return {"asset_list": option.assets}

        assets = AssetModel.query.filter((AssetModel.custom_id == "") | (AssetModel.custom_id == None)).order_by(
            AssetModel.id.desc()).all()
        return {"asset_list": assets}

    @Front.expect({"asset": admin_asset_field})
    @marshal_with(front_asset_field)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('asset', type=dict, help="등록 하려는 옵션 정보", default=None)
        new_asset = parser.parse_args()["asset"]
        # try:
        response_asset = AssetModel(**new_asset)
        db.session.add(response_asset)
        db.session.commit()
        print(response_asset.id)
        return response_asset


@Front.route('product')
class ProductResponse(Resource):
    @Front.response(200, 'Success', front_product_list_field)
    @marshal_with(front_product_list_field)
    def get(self):
        products = ProductModel.query.order_by(ProductModel.id.asc()).all()
        print(products)
        return {"product_list": products}


#client = tasks_v2.CloudTasksClient().from_service_account_json("./nike-by-hongdae-1b876df98ff1.json")

project = 'nike-by-hongdae'
queue = 'de-identify-24hour'
location = 'asia-northeast3'
in_seconds = 1 * 60


@Front.route('order')
class OrderResponse(Resource):
    @Front.expect({'order': front_order_field})
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('order', type=dict, help="주문 객체 (order_field 참조)")
            order = parser.parse_args()["order"]
            asset_list = order["assets"]["asset_list"]
            del order["assets"]
            new_order = OrderModel(**order, status="order")
            db.session.add(new_order)
            for asset in asset_list:
                print(asset['id'])
                print(AssetModel.query.get(asset['id']))
                db.session.add(OrderAssetMap(asset_id=AssetModel.query.get(asset['id']).id, order_id=new_order.id))
            db.session.commit()
            sms_data["receiver"] = order["phone"]
            sms_data["destination"] = order["phone"] + '|' + order["name"]
            send_response = requests.post(send_url, data=sms_data)
            print(send_response)

            # task = {
            #     'app_engine_http_request': {  # Specify the type of request.
            #         'http_method': tasks_v2.HttpMethod.POST,
            #         'relative_uri': '/deidentify',
            #         'body': json.dumps({"key": os.environ['PUBSUB_VERIFICATION_TOKEN'], "id": new_order.id}).encode()
            #     },
            #     'schedule_time': timestamp_pb2.Timestamp().FroomDateTime(
            #         datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=in_seconds))
            # }
            # client.create_task(parent=client.queue_path(project, location, queue), task=task)

            return {"result": True}
        except Exception as e:
            print('error')
            db.session.rollback()
            print(e)

@Front.route('upload')
class UploadFile(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('images', type=FileStorage, location='files', action='append')
        args = parser.parse_args()
        images = args['images']

        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                save_path = os.path.join('static/resource', filename)
                image.save(save_path)
                host_url = request.host_url  # 현재 호스트의 URL을 가져옴
                image_url = f"{host_url}{save_path}"  # 이미지의 URL을 생성
        return {"img": image_url}
        # return {"result": False}, 400


@Front.route('signed')
class UploadFile(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('images', type=FileStorage, location='files', action='append')
        args = parser.parse_args()
        images = args['images']

        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                save_path = os.path.join('static/img', filename)
                image.save(save_path)
                host_url = request.host_url  # 현재 호스트의 URL을 가져옴
                image_url = f"{host_url}{save_path}"  # 이미지의 URL을 생성
        return {"url": image_url}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

"""
@Front.route('upload')
class UploadFile(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('images', type=FileStorage, location='files', action='append')
        args = parser.parse_args()
        images = args['images']
        storage_client = storage.Client.from_service_account_json("./nike-by-hongdae-1b876df98ff1.json")
        bucket = storage_client.get_bucket("nike-by-hongdae-front")
        for image in images:
            extension = image.filename.split('.')[-1]
            if extension in ['jpg', 'jpeg', 'png']:
                blob = bucket.blob('resource/' + image.filename)
                blob.upload_from_string(
                    image.read(),
                    content_type=image.content_type
                )

                return {"img": "https://storage.googleapis.com/nike-by-hongdae-front/resource/" + image.filename}
        storage_client = storage.Client.from_service_account_json("./fig-external-web-6eb3aad467d9.json")
        bucket = storage_client.get_bucket("nike-shoe-finder-front-bucket")
        for image in images:
            extension = image.filename.split('.')[-1]
            if extension in ['jpg', 'jpeg', 'png', 'gif', 'svg']:
                image.save('static/img/{0}'.format(image.filename))
                blob = bucket.blob('static/img/' + image.filename)
                blob.upload_from_string(
                    image.read(),
                    content_type=image.content_type
                )
                # blob.make_public()

                db.session.commit()

                return {"img": 'static/img/{0}'.format(image.filename)}
        return {"result": False}, 400

@Front.route('signed')
class UploadFile(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('images')
        args = parser.parse_args()
        image = args['images']
        
        
        storage_client = storage.Client.from_service_account_json("./nike-by-hongdae-1b876df98ff1.json")
        bucket = storage_client.get_bucket("nike-by-hongdae-front")
        print(image)
        extension = image.split('.')[-1]
        if extension in ['png']:
            blob = bucket.blob(image)
            url = blob.generate_signed_url(
                version="v4",
                # This URL is valid for 15 minutes
                expiration=datetime.timedelta(minutes=15),
                # Allow PUT requests using this URL.
                method="PUT",
                content_type="application/octet-stream",
            )
            return {"url": url}
"""

