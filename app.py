# Проект Строительный магазин
from flask import Flask, session, redirect, url_for
from config import Config
from routers.routers import router
from utils.db import db
from models.models import (User, Product,
                           Category, Cart,
                           CartProduct, Order)
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.register_blueprint(blueprint=router)
app.config.from_object(obj=Config)
db.init_app(app=app)


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if session:
            email = session['email']
            user = User.query.filter_by(email=email).first()
            if user.isAdmin:
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('routers.home'))


admin = Admin(app=app,
              index_view=MyAdminIndexView(name='Главная', url='/admin'),
              name='Админ-панель',
              template_mode='bootstrap4')


class ProductView(ModelView):
    column_display_pk = True  # optional, but I like to see the IDs in the list
    column_searchable_list = ['product_name',
                              'description',
                              'image_path',
                              'product_count',
                              'product_price',
                              ]
    column_hide_backrefs = False
    form_columns = ['product_name', 'description', 'image_path', 'product_count', 'product_price', 'category']


class CustomView(ModelView):
    column_display_pk = True  # optional, but I like to see the IDs in the list
    column_hide_backrefs = False


admin.add_view(CustomView(model=User, session=db.session, name='Пользователи'))
admin.add_view(ProductView(model=Product, session=db.session, name='Товары'))
admin.add_view(CustomView(model=Category, session=db.session, name='Категории'))
admin.add_view(CustomView(model=Cart, session=db.session, name='Корзина'))
admin.add_view(CustomView(model=CartProduct, session=db.session, name='Продукты в корзинах'))
admin.add_view(CustomView(model=Order,session=db.session, name='Заказы'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
