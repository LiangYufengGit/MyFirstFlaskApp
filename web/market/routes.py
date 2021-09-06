from logging import log
from market.forms import RegisterForm
from market import app
from flask import render_template, redirect, url_for, flash, get_flashed_messages,request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market', methods =['GET','POST'])
@login_required #Require user to register before going to this page
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    #follow code is replace by if request.method =="POST"
    #because otherwise alwayse popup
    # if purchase_form.validate_on_submit():
    #     print(request.form.get('purchased_item'))

    if request.method =="POST":
        #purchase item logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations ! You purchased {p_item_object.name} for {p_item_object.price}", category="success")
            else: 
                flash(f"Unforthunatly you don't have enough money to purchase {p_item_object.name}", category="danger")

        #Sell item logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations ! Your item {s_item_object.name} is sold back to market ", category="success")
            else:
                flash(f"Something went wrong with selling {s_item_object.name}")
        return redirect(url_for('market_page'))
        
    if request.method =="GET":
        items = Item.query.filter_by(owner=None)
        owned_items =Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items = items, purchase_form = purchase_form, selling_form = selling_form, owned_items=owned_items)

@app.route('/register', methods =['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():#if user click on the submit button; Validate each filed if caracter not depasse the length 
        user_to_create = User(username= form.username.data, 
                            email_address= form.email_address.data, 
                            password=form.password1.data) 
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created sucessfully ! You are logged in as :{user_to_create.username}', category='success')

        return redirect(url_for('market_page'))
    if form.errors != {}: # form.errors is a dictonary of errors
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user : {err_msg}', category='danger')
            

    return render_template('register.html', form =form)


@app.route('/login', methods =['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username = form.username.data).first() #check if user exists in db
        if attempted_user and attempted_user.check_password_correction( # if user exists and the passowrd hased is matching with DB hased password
            attempted_password = form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success ! You are looged in as :{attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match ! Please try again !')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out !", category='info')
    return redirect(url_for("home_page"))