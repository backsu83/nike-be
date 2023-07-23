from flask_restx import fields, Namespace

Admin = Namespace(
    name="Admin",
    description="관리자 API",
)


Front = Namespace(
    name="Front",
    description="사용자 API",
)


front_asset_field = Front.model('에셋 정보', {
    'id': fields.Integer,
    "category": fields.String(description="작업 분류", required=True),
    "price": fields.Integer(description="에셋 별 가격", required=True),
    "img": fields.String(description="에셋 이미지 주소", required=True),
    "img_back": fields.String(description="에셋 이미지 주소", required=True),
    "custom_id": fields.String(description="에셋 이미지 주소", required=True),
    "registered_at": fields.DateTime(),
})

front_option_field = Front.model('옵션 정보', {
    'id': fields.Integer(),
    "size": fields.String(description="사이즈", required=True),
    "color": fields.String(description="색상", required=True),
    "price": fields.Integer(description="옵션 별 가격", required=True),
    'img': fields.String(description="이미지 주소", required=True),
    "img_back": fields.String(description="이미지 주소", required=True),
    "registered_at": fields.DateTime(),
    "assets": fields.Nested(front_asset_field)
})


admin_asset_field = Admin.model('에셋 등록 정보', {
    "category": fields.String(description="작업 분류", required=True),
    "price": fields.Integer(description="에셋 별 가격", required=True),
    "img": fields.String(description="에셋 이미지 주소", required=True),
    "img_back": fields.String(description="에셋 이미지 뒷면 주소", required=True),
    "options": fields.Nested(front_option_field)
})

front_asset_list_field = Front.model('에셋 리스트 정보', {
    "asset_list": fields.List(fields.Nested(front_asset_field))
})

front_order_field = Front.model('주문 등록 정보', {
    # "name": fields.String(descriptio="고객", required=True),
    "phone": fields.String(description="고객 휴대 전화 번호", required=True),
    "is_agreed": fields.Boolean(description="고객 휴대 전화 번호", required=True),
    "fabric_json": fields.String(description="fabric", required=True),
    "status": fields.String(description="status", required=True),
    "option_id": fields.Integer(description="ID", required=True),
    "assets": fields.List(fields.Nested(front_asset_field)),
    "category": fields.String(description="작업 범주", required=True),
    "img": fields.String(description="URL Address of Upload image (ref. /upload )"),
    "img_back": fields.String(description="URL Address of Upload image (ref. /upload )"),
    "work_img": fields.String(description="URL Address of Upload image (ref. /upload )"),
    "work_img_back": fields.String(description="URL Address of Upload image (ref. /upload )"),
})

admin_option_field = Admin.model('옵션 등록 정보', {
    "id": fields.Integer(description="ID", required=True),
    "size": fields.String(description="사이즈", required=True),
    "color": fields.String(description="색상", required=True),
    "price": fields.Integer(description="옵션 별 가격", required=True),
    "img": fields.String(description="이미지", required=True),
    "img_back": fields.String(description="이미지 뒷면", required=True),
})

admin_order_field = front_order_field.inherit('주문 정보', front_order_field, {
    'id': fields.Integer,
    "modified_at": fields.DateTime()
})

admin_order_list_field = Admin.model('주문 목록', {
    "order_list": fields.List(fields.Nested(admin_order_field))
})

admin_option_list_field = Admin.model('옵션 목록', {
    "option_list": fields.List(fields.Nested(admin_option_field))
})


admin_product_field = Admin.model('제품 등록 정보', {
    "thumbnail": fields.String(description="제품명", required=True),
    "price": fields.Integer(description="제품 가격", required=True),
    "name": fields.String(description="이름", required=True),
    "category": fields.String(description="작업 분류", required=True),
    "img": fields.String(description="이미지 주소", required=True),
    "img_back": fields.String(description="이미지 주소", required=True),
    "masking_x": fields.Integer(description="마스킹 X", required=True),
    "masking_y": fields.Integer(description="마스킹 Y", required=True),
    "masking_width": fields.Integer(description="마스킹 넓이", required=True),
    "masking_height": fields.Integer(description="마스킹 높이", required=True),
    "options": fields.List(fields.Nested(admin_option_field), description="옵션 정보")
})


front_product_field = Front.model('제품 정보', {
    'id': fields.Integer,
    "thumbnail": fields.String(descriptio="제품명", required=True),
    "price": fields.Integer(description="제품 가격", required=True),
    "masking_x": fields.Integer(description="마스킹 X", required=True),
    "masking_y": fields.Integer(description="마스킹 Y", required=True),
    "masking_width": fields.Integer(description="마스킹 넓이", required=True),
    "masking_height": fields.Integer(description="마스킹 높이", required=True),
    "name": fields.String(description="이름", required=True),
    "category": fields.String(description="작업 분류", required=True),
    "img": fields.String(description="이미지 주소", required=True),
    "img_back": fields.String(description="이미지 주소", required=True),
    "options": fields.List(fields.Nested(front_option_field), description="옵션 정보"),
    "registered_at": fields.DateTime()
})
front_product_list_field = Front.model('제품 목록', {"product_list": fields.List(fields.Nested(front_product_field))})
