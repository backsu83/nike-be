from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class AssetModel(db.Model):
    __tablename__ = 'asset'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.Text())
    price = db.Column(db.Integer())
    img = db.Column(db.Text())
    img_back = db.Column(db.Text())
    registered_at = db.Column(db.Time(timezone=True), server_default=db.func.now())
    modified_at = db.Column(db.Time(timezone=True), server_default=db.func.now())
    name = db.Column(db.Text())
    orders = db.relationship("OrderModel", secondary="order_asset_map")
    options = db.relationship("OptionModel", secondary="option_asset_map")
    custom_id = db.Column(db.Text(), server_default=db.func.uuid_generate_v4())


class OptionModel(db.Model):
    __tablename__ = 'option'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    size = db.Column(db.Text())
    color = db.Column(db.Text())
    price = db.Column(db.Integer())
    img = db.Column(db.Text())
    img_back = db.Column(db.Text())
    product_id = db.Column(db.Integer(), db.ForeignKey('product.id'))
    registered_at = db.Column(db.Time(timezone=True), server_default=db.func.now())
    assets = db.relationship("AssetModel", secondary="option_asset_map")
    modified_at = db.Column(db.Time(timezone=True), server_default=db.func.now())


class ProductModel(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    thumbnail = db.Column(db.Text())
    price = db.Column(db.Integer())
    name = db.Column(db.Text())
    code = db.Column(db.Text(), server_default=db.func.uuid_generate_v4())
    category = db.Column(db.Text())
    img = db.Column(db.Text())
    img_back = db.Column(db.Text())
    registered_at = db.Column(db.Time(timezone=True), server_default=db.func.now())
    modified_at = db.Column(db.Time(timezone=True), server_default=db.func.now())
    options = db.relationship('OptionModel', backref='product', order_by=OptionModel.id.asc())
    masking_x = db.Column(db.Integer())
    masking_y = db.Column(db.Integer())
    masking_width = db.Column(db.Integer())
    masking_height = db.Column(db.Integer())


class OrderModel(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_at = db.Column(db.Time(timezone=True), server_default=db.func.now())
    name = db.Column(db.Text())
    phone = db.Column(db.Text())
    is_agreed = db.Column(db.Boolean())
    status = db.Column(db.Text())
    img = db.Column(db.Text())
    work_img = db.Column(db.Text())
    img_back = db.Column(db.Text())
    work_img_back = db.Column(db.Text())
    fabric_json = db.Column(db.Text())
    modified_at = db.Column(db.Time(timezone=True), server_default=db.func.now())
    option_id = db.Column(db.Integer(), db.ForeignKey('option.id'))
    category = db.Column(db.Text())
    assets = db.relationship("AssetModel", secondary="order_asset_map")


class OrderAssetMap(db.Model):
    __tablename__ = 'order_asset_map'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('order.id'))
    asset_id = db.Column(db.Integer(), db.ForeignKey('asset.id'))
    registered_at = db.Column(db.Time(timezone=True), server_default=db.func.now())
    modified_at = db.Column(db.Time(timezone=True), server_default=db.func.now())
    order = db.relationship(OrderModel, backref=db.backref("order_asset_map", cascade="all, delete-orphan"))
    asset = db.relationship(AssetModel, backref=db.backref("order_asset_map", cascade="all, delete-orphan"))


class UserModel(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text())
    phone = db.Column(db.Text())
    password = db.Column(db.Text())
    registered_at = db.Column(db.Time(timezone=True), server_default=db.func.now())
    modified_at = db.Column(db.Time(timezone=True), server_default=db.func.now())
    is_authenticated = db.Column(db.Boolean())
    is_active = db.Column(db.Boolean())
    is_anonymous = db.Column(db.Boolean())

    def get_id(self):
        return self.id


class OptionAssetMap(db.Model):
    __tablename__ = 'option_asset_map'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    option_id = db.Column(db.Integer(), db.ForeignKey('option.id'))
    registered_at = db.Column(db.Time(timezone=True), server_default=db.func.now())
    asset_id = db.Column(db.Integer(), db.ForeignKey('asset.id'))
    option = db.relationship(OptionModel,  backref=db.backref("option_asset_map", cascade="all, delete-orphan"))
    asset = db.relationship(AssetModel, backref=db.backref("option_asset_map", cascade="all, delete-orphan"))

