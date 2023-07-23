from flask_restx import Resource, Namespace, fields, marshal_with, reqparse
from models import db, ProductModel, OptionModel, AssetModel, OrderModel, UserModel, OrderAssetMap, OptionAssetMap

from routers.fields import admin_product_field, admin_order_list_field, admin_order_field, \
    admin_option_field, admin_option_list_field, admin_asset_field, front_asset_list_field, front_asset_field

from flask_login import LoginManager, login_required, logout_user, login_user
from flask_bcrypt import Bcrypt
from routers.fields import Admin

import datetime
# from datetime import datetime

from io import BufferedReader
from io import BytesIO

import urllib.request
import requests
from pytz import timezone

KST = timezone('Asia/Seoul')

send_url = 'https://apis.aligo.in/send/'

sms_data = {'key': '3j5md0dzzts07d2li4yh0tqtwpo55c9m',  # api key
            'userid': 'figcoltd',  # 알리고 사이트 아이디
            'sender': '02-333-2094',  # 발신번호
            'msg': 'NIKE BY YOU\n나이키 스타일 홍대\n주문하신 커스텀이 완료되었습니다.\n직원에게 문의하여 제품을 픽업해 주세요.',  # 문자 내용
            #'msg': 'NIKE BY YOU\n나이키 스타일 홍대\n%고객명%님 주문하신 커스텀이 완료되었습니다.\n직원에게 문의하여 제품을 픽업해 주세요.',  # 문자 내용
            'msg_type': 'LMS',  # 메세지 타입 (SMS, LMS)
            'title': 'NIKE DO IT YOURSELF <홍대점>',  # 메세지 제목 (장문에 적용)
            # 'rdate' : '예약날짜',
            # 'rtime' : '예약시간',
            # 'testmode_yn' : '' #테스트모드 적용 여부 Y/N
            }
 
login_manager = LoginManager()
bcrypt = Bcrypt()

CATEGORY_CLASS = ['print', 'QR', 'laser', 'embroidery']
ORDER_STATE = ['order', 'paid', 'wip', 'done', 'taken']


@Admin.route('product')
class ProductResponse(Resource):
    @login_required
    @Admin.expect(admin_product_field)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('product', type=dict, help="등록 하려는 상품 정보", default=None)
        new_product = parser.parse_args()["product"]

        # try:
        db.session.add(ProductModel(**new_product))
        db.session.commit()
        return {"result": True}
        # except TypeError as E:
        #     print(E)
        #     return {"result": False, "error": 'db type error'}, 400

    @login_required
    @Admin.expect(admin_product_field)
    @Admin.response(200, 'Success')
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('product', type=dict, help="수정 하려는 상품 정보", default=None)
        new_product = parser.parse_args()["product"]
        try:
            product = ProductModel.query.get(new_product["id"])
            print(product)
            if product is None:
                return {"result": False}, 404
            db.session.merge(ProductModel(**new_product))
            db.session.commit()
            return {"result": True}
        except Exception as E:
            print(E)

            db.session.rollback()
            return {"result": False, "error": 'db type error'}, 400

    @login_required
    @Admin.expect(admin_product_field)
    @Admin.response(200, 'Success')
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', help="삭제 하려는 상품 ID", type=int, default=None)
        index = parser.parse_args()["id"]
        # try:
        find_product = ProductModel.query.get(index)
        if find_product is None:
            return {"result": False}, 404
        db.session.delete(find_product)
        db.session.commit()
        return {"result": True}

        # except Exception as E:
        #     return {"result": False, "error": 'db type error'}, 400


@Admin.route('option')
class OptionResponse(Resource):
    @login_required
    @Admin.response(200, 'Success')
    @marshal_with(admin_option_list_field)
    def get(self):
        # parser = reqparse.RequestParser()
        # parser.add_argument('id', help="주문 번호")
        # order_id = parser.parse_args()["id"]

        return {"option_list": OptionModel.query.order_by(OptionModel.id.desc()).all()}

    @login_required
    @Admin.expect(admin_option_field)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('option', type=dict, help="등록 하려는 옵션 정보", default=None)
        new_option = parser.parse_args()["option"]

        # try:
        db.session.add(OptionModel(**new_option))

        db.session.commit()
        return {"result": True}
        # except TypeError as E:
        #     print(E)
        #     return {"result": False, "error": 'db type error'}, 400

    @login_required
    @Admin.doc(params={'product': '업데이트하려는 product 정보 (admin_product_field model 참조)'})
    @Admin.response(200, 'Success')
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('option', type=dict, help="수정 하려는 옵션 정보", default=None)
        new_option = parser.parse_args()["option"]
        try:
            option = OptionModel.query.get(new_option["id"])
            print(option)
            if option is None:
                return {"result": False}, 404
            new_assets = new_option["assets"]
            del new_option["assets"]
            db.session.merge(OptionModel(**new_option))

            if new_assets is not None:
                print(new_assets)
                OptionAssetMap.query.filter(OptionAssetMap.option_id == option.id).delete()
                for asset in new_assets:
                    db.session.add(OptionAssetMap(option_id=option.id, asset_id=asset["id"]))
            db.session.commit()
            return {"result": True}
        except Exception as E:
            db.session.rollback()
            return {"result": False}, 500

    @login_required
    @Admin.doc(params={'id': '삭제 하려는 에셋 ID'})
    @Admin.response(200, 'Success')
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', help="삭제 하려는 에셋 ID", type=int, default=None)
        index = parser.parse_args()["id"]
        # try:
        find_option = OptionModel.query.get(index)
        if find_option is None:
            return {"result": False}, 404
        db.session.delete(find_option)
        db.session.commit()
        return {"result": True}


@Admin.route('asset')
class OptionResponse(Resource):
    @login_required
    @Admin.expect(admin_asset_field)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('asset', type=dict, help="등록 하려는 에셋 정보", default=None)
        new_asset = parser.parse_args()["asset"]

        # try:
        db.session.add(AssetModel(**new_asset, custom_id=""))
        db.session.commit()
        return {"result": True}
        # except TypeError as E:
        #     print(E)
        #     return {"result": False, "error": 'db type error'}, 400

    @login_required
    @Admin.doc(params={'asset': '업데이트하려는 에셋 정보 (front_asset_field model 참조)'})
    @Admin.response(200, 'Success')
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('asset', type=dict, help="수정 하려는 에셋 정보", default=None)
        new_asset = parser.parse_args()["asset"]
        # try:
        asset = AssetModel.query.get(new_asset["id"])
        print(asset)
        if asset is None:
            return {"result": False}, 404
        db.session.merge(AssetModel(**new_asset))
        db.session.commit()
        return {"result": True}
        # except Exception as E:
        #     print(E)
        #     return {"result": False, "error": 'db type error'}, 400

    @login_required
    @Admin.doc(params={'id': '삭제 하려는 에셋 ID'})
    @Admin.response(200, 'Success')
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', help="삭제 하려는 에셋 ID", type=int, default=None)
        index = parser.parse_args()["id"]
        # try:
        find_option = AssetModel.query.get(index)
        if find_option is None:
            return {"result": False}, 404
        db.session.delete(find_option)
        db.session.commit()
        return {"result": True}

        # except Exception as E:
        #     return {"result": False, "error": 'db type error'}, 400


@Admin.route('order')
# @Admin.doc(params={'id': '주문 번호'})
class OrderResponse(Resource):
    @login_required
    @Admin.response(200, 'Success')
    @marshal_with(admin_order_list_field)
    def get(self):
        parser = reqparse.RequestParser()
        # parser.add_argument('id', help="주문 번호")
        # order_id = parser.parse_args()["id"]
        parser.add_argument('start', type=str, location='args', help="시작 일자")
        parser.add_argument('end', type=str, location='args', help="끝 일자")
        parser.add_argument('keyword', type=str, location='args', help="끝 일자")
        parser.add_argument('status', type=str, location='args', help="끝 일자")
        start = parser.parse_args()["start"]
        end = parser.parse_args()["end"]
        keyword = parser.parse_args()["keyword"]
        status = parser.parse_args()["status"]

        query_result = OrderModel.query


        order_list = OrderModel.query.filter(OrderModel.modified_at+datetime.timedelta(days=1) < datetime.datetime.now()).filter(OrderModel.modified_at >= datetime.datetime.now()-datetime.timedelta(days=3)).order_by(OrderModel.modified_at.desc()).all()

        for order in order_list:
            order.name = ""
            order.phone = '010-****-'+order.phone.split('-')[-1]
            db.session.merge(order)

        db.session.commit()

        try:
            if start is not None:
                #start_date = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                #start_date.replace(tzinfo=KST)
                query_result = query_result.filter(OrderModel.modified_at >= start)
            if end is not None:
                #end_date = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
                #end_date.replace(tzinfo=KST)
                query_result = query_result.filter(OrderModel.modified_at <= end)
            if keyword is not None:
                query_result = query_result.filter(
                    OrderModel.name.contains(keyword) | OrderModel.phone.contains(keyword))
            if status is not None:
                query_result = query_result.filter(status=status)
            query_result = query_result.order_by(OrderModel.modified_at.desc()).all()
            for order in query_result :
                order.phone = '010-****-'+order.phone.split('-')[-1]
            return {
                "order_list": query_result
            }
        except:
            # db.session.close()
            return {"result": False}, 400

    @login_required
    @Admin.doc(params={'order': '업데이트 하려는 order 정보 (admin_order_field model 참조)'})
    @Admin.response(200, 'Success')
    # @Admin.expect({'order': admin_order_field})
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('order', type=dict, help="주문 객체 (admin_order_field 참조)")
        order = parser.parse_args()["order"]
        asset_list = order["assets"]["asset_list"]
        del order["assets"]
        if order["status"] == 'done':
            new_order = OrderModel.query.get(order['id'])
            sms_data["receiver"] = new_order.phone
            sms_data["destination"] = new_order.phone + '|' + new_order.name
            send_response = requests.post(send_url, data=sms_data)
            print(send_response.json())
        new_order = OrderModel(**order)
        db.session.merge(new_order)
        for asset in asset_list:
            db.session.add(OrderAssetMap(asset_id=AssetModel.query.get(asset['id']).id, order_id=new_order.id))
        db.session.commit()
        return {"result": True}


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(user_id)


@Admin.route('login')
@Admin.doc(params={'id': 'ID', 'pw': '비밀번호'})
class LoginResponse(Resource):
    @Admin.expect(
        {"id": fields.String(description='id', required=True), "pw": fields.String(description='비밀번호', required=True)})
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', help="관리자 계정")
        parser.add_argument('pw', type=str, help="관리자 암호")
        account = parser.parse_args()["id"]
        password = parser.parse_args()["pw"]

        if account is None or password is None:
            return {'result': False}, 400
        # gen figmarlion!0704
        # db.session.add(
        #     UserModel(name="4dm1n",
        #               phone="010-8794-3835",
        #               password=bcrypt.generate_password_hash('figmarlion!0704'.encode("utf-8")).decode("utf-8")
        #               )
        # )
        # db.session.commit()
        user = UserModel.query.filter_by(name=account).first()
        if user is None:
            return {'result': False}, 404

        login_success = bcrypt.check_password_hash(user.password.encode("utf-8"), password.encode("utf-8"))

        if login_success:
            return {'result': login_user(user=user, remember=True)}

        return {'result': False}, 403


@Admin.route('logout')
class LoginResponse(Resource):
    @login_required
    def get(self):
        logout_user()
        return {"result": True}


@Admin.route('message')
class MessageResponse(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('order', type=dict, help="주문 객체 (admin_order_field 참조)")
        order = parser.parse_args()["order"]

        new_order = OrderModel.query.get(order['id'])

        sms_data["receiver"] = new_order.phone
        sms_data["msg"] = order["msg"]
        
        if order["msg_type"] == 'MMS':
            sms_data["msg_type"] = "MMS"

            req = urllib.request.Request(order["path"], headers = {"User-Agent" : "Mozilla/5.0"})
            res = urllib.request.urlopen(req).read()

            #files = {'image' : open('./upload.png','rb')}
            files = {'image' : ('message.png', BufferedReader(BytesIO(res)), 'image/png', {'Expires': '0'})}
            send_response = requests.post(send_url, data=sms_data, files = files)
            return {"result": True}
        else:
            sms_data["msg_type"] = "LMS"
            send_response = requests.post(send_url, data=sms_data)

        return {"result": True}

