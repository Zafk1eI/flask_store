from flask import render_template, Blueprint, request, flash, url_for, redirect, session, abort
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from utils.db import db
from sqlalchemy.exc import IntegrityError
from models.models import (User, Product, Cart,
                           CartProduct, Category,
                           Order)

router = Blueprint('routers', __name__)


@router.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@router.route('/')
@router.route('/home')
def home():
    # получить все товары и категории
    products = Product.query.all()
    categories = Category.query.all()
    if 'email' in session:
        email = session['email']
        # получить пользователя по электронной почте
        user = User.query.filter_by(email=email).first()
        is_admin = user.isAdmin if user else False
        return render_template('index.html',
                               email=session['email'],
                               admin=is_admin,
                               products=products, user_id=user.user_id, categories=categories)
    else:
        return render_template('index.html')


@router.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        password = request.form['password']

        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['email'] = email
            user_cart = Cart.query.filter_by(User_user_id=user.user_id).first()
            # запрос на добавление пользователю корзины
            if not user_cart:
                add_cart = Cart(User_user_id=user.user_id)
                db.session.add(add_cart)
                db.session.commit()
            return redirect(url_for('routers.home'))
    return render_template('login.html')


@router.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conf_password = request.form['confirm-password']

        # Проверяем, существует ли пользователь с таким email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Пользователь с таким email уже зарегистрирован')
            return redirect(url_for('routers.register'))

        if password == conf_password:
            pass_hash = generate_password_hash(password=password)
            user = User(email=email, password=pass_hash)
            try:
                db.session.add(user)
                db.session.commit()
                flash('Успешно зарегистрировались')
                return redirect(url_for('routers.login'))
            except IntegrityError:
                db.session.rollback()
                flash('Ошибка записи в базу данных')
        else:
            flash('Пароли не совпадают')
    return render_template('register.html')


@router.route('/cart/<int:cart_id>')
def cart(cart_id):
    if 'email' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(email=session['email']).first()
    if not user or user.cart.cart_id != cart_id:
        print('Не работает')
        abort(404)
    cart_products = CartProduct.query.filter_by(cart_cart_id=cart_id).all()
    products = [cart_product.product for cart_product in cart_products]
    print(products)
    total = 0
    for item in products:
        total += item.product_price
    return render_template('cart.html', user_id=user.user_id,
                           email=session['email'], cart_products=products,
                           total_price=total, end_price=total + 200)


@router.route('/categories/<int:category_id>')
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    products = category.products
    categories = Category.query.all()
    if 'email' in session:
        email = session['email']
        user = User.query.filter_by(email=email).first()
        is_admin = user.isAdmin if user else False
        return render_template('index.html',
                               email=session['email'],
                               admin=is_admin, user_id=user.user_id,
                               products=products,
                               categories=categories)
    else:
        return render_template('index.html')


@router.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'email' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(email=session['email']).first()
    if not user:
        abort(404)
    cart_product = CartProduct.query.filter_by(cart_cart_id=user.cart.cart_id, product_product_id=product_id).first()
    if not cart_product:
        cart_product = CartProduct(product_product_id=product_id, cart_cart_id=user.cart.cart_id)
        db.session.add(cart_product)
        db.session.commit()
    else:
        flash('Товар уже добавлен в корзину')

    return redirect(url_for('routers.cart', cart_id=user.cart.cart_id))


@router.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_product_from_cart(product_id):
    if 'email' not in session:
        flash("Вы не авторизованы")
    user = User.query.filter_by(email=session['email']).first()
    if not user:
        flash('Пользователь не найден')
    cart_product = CartProduct.query.filter_by(cart_cart_id=user.cart.cart_id, product_product_id=product_id).first()
    if not cart_product:
        flash('Товар не найден в корзине')

    db.session.delete(cart_product)
    db.session.commit()

    return redirect(url_for('routers.cart', cart_id=user.cart.cart_id))


@router.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('routers.login'))


@router.route('/product_details/<int:product_id>')
def product_details(product_id):
    if 'email' not in session:
        redirect(url_for("routers.login"))
    product = Product.query.filter_by(product_id=product_id).first()
    user = User.query.filter_by(email=session['email']).first()
    if not product:
        flash('Товар не найден')
    return render_template('product_details.html', product=product,
                           email=session['email'], user_id=user.user_id)


@router.route('/checkout')
def create_order():
    # Проверяем, вошел ли пользователь в систему
    if 'email' not in session:
        return redirect(url_for('routers.login'))

    # Получаем пользователя
    user = User.query.filter_by(email=session['email']).first()
    if not user:
        # Если пользователь не найден, перенаправляем на страницу входа
        return redirect(url_for('router.login'))

    # Получаем продукты в корзине пользователя
    cart_products = CartProduct.query.filter_by(cart_cart_id=user.cart.cart_id).all()

    for cart_product in cart_products:
        order_product = Order(
            user_id=user.user_id,
            product_id=cart_product.product_product_id,
            quantity=1,
            price=cart_product.product.product_price
        )
        db.session.add(order_product)
        product = cart_product.product
        product.product_count -= 1

    # Очищаем корзину пользователя
    CartProduct.query.filter_by(cart_cart_id=user.cart.cart_id).delete()
    db.session.commit()

    flash('Заказ успешно сформирован!')

    # Перенаправляем пользователя на главную страницу
    return redirect(url_for('routers.home'))


@router.route('/report')
def report():
    user = User.query.filter_by(email=session['email']).first()
    return render_template('report.html',
                           user_id=user.user_id,
                           email=session['email'])


@router.route('/most_popular')
def generate_report():
    user = User.query.filter_by(email=session['email']).first()
    most_popular_product = (
        db.session.query(
            Product.product_id, Product.product_name, func.sum(Order.quantity).label('total_quantity'))
        .join(Order, Product.product_id == Order.product_id)
        .group_by(Product.product_id, Product.product_name)
        .order_by(func.sum(Order.quantity).desc())
        .all()
    )
    return render_template('report.html', user_id=user.user_id,
                           email=session["email"], products=most_popular_product,
                           first_th='Название товара', report_name='Популярные товары',
                           second_th='Количество заказов')


@router.route('/total_by_category')
def generate_report_total_by_category():
    user = User.query.filter_by(email=session['email']).first()
    total_revenue_by_category = (
        db.session.query(
            Category.id, Category.category_name, func.sum(Order.quantity).label('total_quantity'))
        .join(Product, Category.id == Product.category_id)
        .join(Order, Product.product_id == Order.product_id)
        .group_by(Category.category_name)
        .order_by(func.sum(Order.quantity).desc())
        .all()
    )
    return render_template('report.html', user_id=user.user_id,
                           email=session["email"], products=total_revenue_by_category,
                           first_th='категория', report_name='Выручка по категориям',
                           second_th='Выручка')

