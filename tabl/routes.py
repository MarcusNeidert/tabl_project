import os
import secrets
import random
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from tabl import app, db, bcrypt
from tabl.forms import RegistrationForm, LoginForm, UpdateAccountForm, EditStyleForm, EditCookwareForm, EditIngredientForm
from tabl.models import User, Style, Ingredient, Cookware
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    if (current_user.is_authenticated and (current_user.is_admin == True)):
        return redirect(url_for('admin'))
    else:
        return render_template('home.html')


@app.route("/challenge")
@login_required
def challenge():
    # ADD POSSIBLE OUTCOMES FOR INGREDIENTS
    ok_carbohydrates = []
    ok_proteins      = []
    ok_flavourings   = []
    for carb in Ingredient.query.filter_by(category='carbohydrates'):
        if carb in current_user.user_intolerances:
            continue
        else:
            ok_carbohydrates.append(carb)
    for protein in Ingredient.query.filter_by(category='protein'):
        if protein in current_user.user_intolerances:
            continue
        else:
            ok_proteins.append(protein)
    for flavouring in Ingredient.query.filter_by(category='flavouring'):
        if flavouring in current_user.user_intolerances:
            continue
        else:
            ok_flavourings.append(flavouring)

    # ADD POSSIBLE OUTCOMES FOR STYLE AND COOKWARE
    possible_styles     = []
    possible_cookware   = []
    for style in Style.query.all():
        if style.name == 'I don\u0027t prefer any style':
            continue
        else:
            possible_styles.append(style.name)
    for cookware in Cookware.query.all():
        if cookware in current_user.cookware:
            possible_cookware.append(cookware.name)
        else:
            continue
    # RANDOMIZE AN ELEMENT FROM EACH LIST
    challenge_carb          = random.choice(ok_carbohydrates)
    challenge_protein       = random.choice(ok_proteins)
    challenge_flavouring    = random.choice(ok_flavourings)
    challenge_style         = random.choice(possible_styles)
    challenge_cookware      = random.choice(possible_cookware)
    return render_template('challenge.html', title='Challenge',
                            challenge_carb=challenge_carb,
                            challenge_protein=challenge_protein,
                            challenge_flavouring=challenge_flavouring,
                            challenge_style=challenge_style,
                            challenge_cookware=challenge_cookware)


@app.route("/admin")
def admin():
    return render_template('admin.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form   = RegistrationForm()
    for style in Style.query.all():
        form.user_style.choices.append((style.id, style.name))
    for cookware in Cookware.query.order_by(Cookware.name).all():
        form.user_cookware.choices.append((cookware.id, cookware.name))
    for carb in Ingredient.query.filter_by(category='carbohydrates').order_by(Ingredient.name):
        form.carbs_intolerances.choices.append((carb.id, carb.name))
    for protein in Ingredient.query.filter_by(category='protein').order_by(Ingredient.name):
        form.protein_intolerances.choices.append((protein.id, protein.name))
    for flavouring in Ingredient.query.filter_by(category='flavouring').order_by(Ingredient.name):
        form.flavouring_intolerances.choices.append((flavouring.id, flavouring.name))

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, user_style_id=form.user_style.data)
        if form.user_cookware.data:
            for cookware_id in form.user_cookware.data:
                cookware = Cookware.query.get(cookware_id)
                user.cookware.append(cookware)
            for carb_id in form.carbs_intolerances.data:
                carbs    = Ingredient.query.get(carb_id)
                user.user_intolerances.append(carbs)
            for protein_id in form.protein_intolerances.data:
                proteins = Ingredient.query.get(protein_id)
                user.user_intolerances.append(proteins)
            for flavouring_id in form.flavouring_intolerances.data:
                flavourings = Ingredient.query.get(flavouring_id)
                user.user_intolerances.append(flavourings)
            db.session.add(user)
            try:
                db.session.commit()
                flash('Your account has been created! You are now able to log in', 'success')
                return redirect(url_for('login'))
            except Exception:
                db.session.rollback()
                flash('Something went wrong', 'danger')
                return redirect(url_for('register'))
        else:
            flash('You must have some sort of cookware at home?', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html',
                           title='Register',
                           form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html',
                           title='Login',
                           form=form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_compressed_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def save_raw_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    form_picture.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    # SHOW ALL STYLES CHOICES
    for style in Style.query.all():
        form.update_style.choices.append((style.id, style.name))
    # SHOW ALL COOKWARE CHOICES
    for cookware in Cookware.query.order_by(Cookware.name).all():
        form.update_cookware.choices.append((cookware.id, cookware.name))
    # SHOW ALL INTOLERANCE CHOICES - CARBS
    for carb in Ingredient.query.filter_by(category='carbohydrates').order_by(Ingredient.name):
        form.update_carbs_intolerances.choices.append((carb.id, carb.name))
    # SHOW ALL INTOLERANCE CHOICES - PROTEINS
    for protein in Ingredient.query.filter_by(category='protein').order_by(Ingredient.name):
        form.update_protein_intolerances.choices.append((protein.id, protein.name))
    # SHOW ALL INTOLERANCE CHOICES - FLAVOURINGS
    for flavouring in Ingredient.query.filter_by(category='flavouring').order_by(Ingredient.name):
        form.update_flavouring_intolerances.choices.append((flavouring.id, flavouring.name))

    if form.validate_on_submit():
        if form.picture.data:
            # picture_file = save_compressed_picture(form.picture.data)
            picture_file            = save_raw_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username       = form.username.data
        current_user.email          = form.email.data
        current_user.user_style_id  = form.update_style.data

        # CLEAR PREVIOUS INFORMATION FROM USER
        current_user.user_intolerances.clear()
        current_user.cookware.clear()

        # ADD NEW INPUTS FROM USER
        for cookware_id in form.update_cookware.data:
            cookware    = Cookware.query.get(cookware_id)
            current_user.cookware.append(cookware)
        for carb_id in form.update_carbs_intolerances.data:
            carbs       = Ingredient.query.get(carb_id)
            current_user.user_intolerances.append(carbs)
        for protein_id in form.update_protein_intolerances.data:
            proteins    = Ingredient.query.get(protein_id)
            current_user.user_intolerances.append(proteins)
        for flavouring_id in form.update_flavouring_intolerances.data:
            flavourings = Ingredient.query.get(flavouring_id)
            current_user.user_intolerances.append(flavourings)
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data          = current_user.username
        form.email.data             = current_user.email
        form.update_style.data      = current_user.user_style_id

        current_cookware = []  #CREATING A LIST FOR COOKWARE_ID IN CURRENT USER
        for cookware in current_user.cookware:
            current_cookware.append(cookware.id)
        form.update_cookware.data   = current_cookware #PRECHECKING OPTIONS ALREADY FILLED

        current_intolerances = []
        for intolerance in current_user.user_intolerances:
            #if intolerance.category == 'carbohydrates':
            current_intolerances.append(intolerance.id)
        form.update_carbs_intolerances.data      = current_intolerances
        form.update_protein_intolerances.data    = current_intolerances
        form.update_flavouring_intolerances.data = current_intolerances

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',
                           title='Account',
                           image_file=image_file,
                           form=form)

@app.route("/edit_styles", methods=['GET', 'POST'])
@login_required
def edit_styles():
    if (current_user.is_authenticated and (current_user.is_admin == True)):
        pass
    else:
        return redirect(url_for('home'))
    form   = EditStyleForm()
    for style in Style.query.all():
        form.remove_styles.choices.append((style.id, style.name))

    if form.validate_on_submit():
        for item in form.remove_styles.data:
            style = Style.query.get(item)
            db.session.delete(style)
        if form.new_style.data and form.remove_styles.data:
            db.session.add(Style(name=form.new_style.data.capitalize()))
            try:
                db.session.commit()
                flash(f'{form.new_style.data} added to styles!', 'success')
                flash('Deletion successful', 'success')
            except Exception:
                db.session.rollback()
                flash('Either style exists or users really enjoy this style', 'danger')
        elif form.remove_styles.data:
            try:
                db.session.commit()
                flash('Deletion successful', 'success')
            except Exception:
                db.session.rollback()
                flash('Users really enjoy that style... dufus!', 'danger')
        elif form.new_style.data:
            db.session.add(Style(name=form.new_style.data.capitalize()))
            try:
                db.session.commit()
                flash(f'{form.new_style.data.capitalize()} added to styles!', 'success')
            except Exception:
                db.session.rollback()
                flash('That style already exists!', 'danger')
                return redirect(url_for('edit_styles'))
        else:
            pass
        return redirect(url_for('edit_styles'))
    return render_template('edit_styles.html',
                           title='Edit styles',
                           form=form)


@app.route("/edit_cookware", methods=['GET', 'POST'])
@login_required
def edit_cookware():
    if (current_user.is_authenticated and (current_user.is_admin == True)):
        pass
    else:
        return redirect(url_for('home'))
    form = EditCookwareForm()
    for cookware in Cookware.query.order_by(Cookware.name).all():
        form.remove_cookware.choices.append((cookware.id, cookware.name))
    if form.validate_on_submit():
        for item in form.remove_cookware.data:
            cookware = Cookware.query.get(item)
            db.session.delete(cookware)
        if form.new_cookware.data and form.remove_cookware.data:
            db.session.add(Cookware(name=form.new_cookware.data.capitalize()))
            db.session.commit()
            flash(f'{form.new_cookware.data} added to cookware!', 'success')
            flash('Deletion successful', 'success')
        elif form.remove_cookware.data:
            db.session.commit()
            flash('Deletion successful', 'success')
        elif form.new_cookware.data:
            try:
                db.session.add(Cookware(name=form.new_cookware.data.capitalize()))
                db.session.commit()
                flash(f'{form.new_cookware.data.capitalize()} added to cookware!', 'success')
            except Exception:
                db.session.rollback()
                flash('That cookware already exists!', 'danger')
                return redirect(url_for('edit_cookware'))
        else:
            pass
        return redirect(url_for('edit_cookware'))
    return render_template('edit_cookware.html',
                           title='Edit cookware',
                           form=form)

@app.route("/edit_ingredients", methods=['GET', 'POST'])
@login_required
def edit_ingredients():
    if (current_user.is_authenticated and (current_user.is_admin == True)):
        pass
    else:
        return redirect(url_for('home'))
    form = EditIngredientForm()
    # CREATE CHECKBOX COLUMNS FOR EACH CATEGORY
    for carb in Ingredient.query.filter_by(category='carbohydrates').order_by(Ingredient.name):
        form.remove_carbs.choices.append((carb.id, carb.name))
    for protein in Ingredient.query.filter_by(category='protein').order_by(Ingredient.name):
        form.remove_proteins.choices.append((protein.id, protein.name))
    for flavouring in Ingredient.query.filter_by(category='flavouring').order_by(Ingredient.name):
        form.remove_flavourings.choices.append((flavouring.id, flavouring.name))

    # CREATE LIST OF ALL AVAILABLE CATEGORIES
    for ingredient in Ingredient.query.all():
        if ingredient.category in form.new_ingredient_category.choices:
            continue
        else:
            form.new_ingredient_category.choices.append(ingredient.category)

    if form.validate_on_submit():
        for carb in form.remove_carbs.data:
            ingredient = Ingredient.query.get(carb)
            db.session.delete(ingredient)
        for protein in form.remove_proteins.data:
            ingredient = Ingredient.query.get(protein)
            db.session.delete(ingredient)
        for flavouring in form.remove_flavourings.data:
            ingredient = Ingredient.query.get(flavouring)
            db.session.delete(ingredient)
        if (form.new_ingredient_name.data and form.new_ingredient_category.data and (form.remove_carbs.data or form.remove_proteins.data or form.remove_flavourings.data)):
            db.session.add(Ingredient(name=form.new_ingredient_name.data.capitalize(), category=form.new_ingredient_category.data))
            try:
                db.session.commit()
                flash(f'{form.new_ingredient_name.data.capitalize()} added to ingredients!', 'success')
                flash('Deletion successful', 'success')
            except Exception:
                db.session.rollback()
                flash('That ingredient already exists!', 'danger')
                return redirect(url_for('edit_ingredients'))
        elif form.remove_carbs.data or form.remove_proteins.data or form.remove_flavourings.data:
            db.session.commit()
            flash('Deletion successful', 'success')
        elif form.new_ingredient_name.data and form.new_ingredient_category.data:
            db.session.add(Ingredient(name=form.new_ingredient_name.data.capitalize(), category=form.new_ingredient_category.data))
            try:
                db.session.commit()
                flash(f'{form.new_ingredient_name.data.capitalize()} added to ingredients!', 'success')
            except Exception:
                db.session.rollback()
                flash('That ingredient already exists!', 'danger')
                return redirect(url_for('edit_ingredients'))
        else:
            pass
        return redirect(url_for('edit_ingredients'))
    return render_template('edit_ingredients.html',
                           title='Edit ingredients',
                           form=form)

@app.route("/users", methods=['GET', 'POST'])
@login_required
def users():
    if (current_user.is_authenticated and (current_user.is_admin == True)):
        pass
    else:
        return redirect(url_for('users'))
    if 'keyword' in request.args:
        keyword = request.args['keyword']
        users = User.query.filter(User.username.like(f'%{keyword}%')).order_by(User.username).all()
    else:
        users = User.query.order_by(User.username).all()

    return render_template('users.html',
                           title='Users',
                           users=users)