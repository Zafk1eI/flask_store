from utils.db import db
from datetime import datetime, timezone


# Define the User model
class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    isAdmin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    cart = db.relationship('Cart', uselist=False, backref=db.backref('user'), cascade='all, delete')

    def __str__(self):
        return self.email


# Define the Cart model
class Cart(db.Model):
    __tablename__ = 'cart'

    cart_id = db.Column(db.Integer, primary_key=True)
    User_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    products = db.relationship('CartProduct', backref='cart', lazy='dynamic')


# Define the CartProduct model
class CartProduct(db.Model):
    __tablename__ = 'cart_product'

    id = db.Column(db.Integer, primary_key=True)
    product_product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    cart_cart_id = db.Column(db.Integer, db.ForeignKey('cart.cart_id'))
    product = db.relationship("Product", backref='cartproduct')


# Define the Category model
class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(45), nullable=False, unique=True)

    def __str__(self):
        return self.category_name


# Define the Product model
class Product(db.Model):
    __tablename__ = 'product'

    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(45), nullable=False)
    image_path = db.Column(db.String(50))
    description = db.Column(db.Text)
    product_count = db.Column(db.Integer, default=0, nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref='products')

    def __str__(self):
        return self.product_name


# Модель для продуктов в заказе
class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    products = db.relationship('Product', backref='order')
    user = db.relationship('User', backref='order')
