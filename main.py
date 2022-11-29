"""
-flask-login
-sign up
-sign in (authentication)
"""

from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = "?``§=)()%``ÄLÖkhKLWDO=?)(_:;LKADHJATZQERZRuzeru3rkjsdfLJFÖSJ"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'sign_in'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt(app)

migrate = Migrate(app, db)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    user_orders = db.relationship('UserOrder', back_populates='product')


class UserOrder(db.Model):
    __tablename__ = 'user_order'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product = db.relationship('Product', back_populates='user_orders')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


with app.app_context():
    import forms

    db.create_all()


@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password1.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Registration succeeded, {user.username}, now you can sign in.', 'success')
        return redirect(url_for('index'))
    return render_template('sign_up.html', form=form)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = forms.SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash(f'User {form.username.data} does not exist!', 'danger')
            return redirect(url_for('sign_in'))
        if not bcrypt.check_password_hash(user.password, form.password.data):
            flash(f'User / password do not match!', 'danger')
            return redirect(url_for('sign_in'))
        login_user(user)
        flash(f'Welcome, {user.username}', 'success')
        return redirect(url_for('index'))
    return render_template('sign_in.html', form=form)


@app.route('/sign_out')
def sign_out():
    flash(f'See you next time, {current_user.username}')
    logout_user()
    return redirect(url_for('index'))


@login_required
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = forms.CreateProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, code=form.code.data)
        db.session.add(product)
        db.session.commit()
        flash(f'Product {product.name} created.', 'success')
        return redirect(url_for('add_product'))
    return render_template('add_product.html', form=form)


@app.route('/show_product_item/<product_id>')
def show_product_item(product_id):
    product = Product.query.get(product_id)
    return render_template('show_product_item.html', product=product)


@app.route('/show_products')
def show_products():
    products = Product.query.all()
    return render_template('show_products.html', products=products)


@login_required
@app.route('/add_user_order', methods=['GET', 'POST'])
def add_user_order():
    form = forms.CreateUserOrderForm()
    if form.validate_on_submit():
        order = UserOrder(
            product_id=form.product.data.id
            , quantity=form.quantity.data
            , user_id=current_user.id
        )
        db.session.add(order)
        db.session.commit()
        flash('Order created', 'success')
        return redirect(url_for('add_user_order'))
    return render_template('add_user_order.html', form=form)


@login_required
@app.route('/show_user_orders')
def show_user_orders():
    orders = UserOrder.query.filter_by(user_id=current_user.id).all()
    return render_template('show_user_orders.html', data=orders)


if __name__ == '__main__':
    app.run(debug=True)
