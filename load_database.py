import os
import sys
import requests
from tabl import db, bcrypt
from tabl.models import User, Ingredient, Cookware, Style

host = 'localhost'  # host where the system is running
port = 5000  # port where the process is running


def reload_database():
    exit_reload = False
    try:
        response = requests.get(f'http://{host}:{port}')
        print('The website seems to be running. Please stop it and run this file again.', file=sys.stderr)
        exit_reload = True
    except:
        pass
    if exit_reload:
        exit(11)
    try:
        os.remove('tabl/site.db')
        print('previous DB file removed')
    except:
        print('no previous file found')

    db.create_all()

    # CREATING INGREDIENTS
    # CREATING CARBS
    carb_1 = Ingredient(name='Potatoes',
                              category='carbohydrates')
    carb_2 = Ingredient(name='Rice',
                              category='carbohydrates')
    carb_3 = Ingredient(name='Pasta',
                        category='carbohydrates')
    carb_4 = Ingredient(name='Bread',
                        category='carbohydrates')
    carb_5 = Ingredient(name='Bulgur',
                        category='carbohydrates')
    carb_6 = Ingredient(name='Couscous',
                        category='carbohydrates')
    carb_7 = Ingredient(name='Quinoa',
                        category='carbohydrates')

    db.session.add(carb_1)
    db.session.add(carb_2)
    db.session.add(carb_3)
    db.session.add(carb_4)
    db.session.add(carb_5)
    db.session.add(carb_6)
    db.session.add(carb_7)

    # CREATING PROTEINS
    protein_1 = Ingredient(name='Chicken',
                              category='protein')
    protein_2 = Ingredient(name='Tofu',
                           category='protein')
    protein_3 = Ingredient(name='Pork',
                           category='protein')
    protein_4 = Ingredient(name='Beef',
                           category='protein')
    protein_5 = Ingredient(name='Mushroom',
                           category='protein')
    protein_6 = Ingredient(name='Scallops',
                           category='protein')
    protein_7 = Ingredient(name='Shrimp',
                           category='protein')

    db.session.add(protein_1)
    db.session.add(protein_2)
    db.session.add(protein_3)
    db.session.add(protein_4)
    db.session.add(protein_5)
    db.session.add(protein_6)
    db.session.add(protein_7)

    # CREATING FLAVOURINGS
    flavouring_1 = Ingredient(name='Thyme',
                              category='flavouring')
    flavouring_2 = Ingredient(name='Garlic',
                             category='flavouring')
    flavouring_3 = Ingredient(name='Chili',
                             category='flavouring')
    flavouring_4 = Ingredient(name='Cloves',
                              category='flavouring')
    flavouring_5 = Ingredient(name='Cumin',
                              category='flavouring')
    flavouring_6 = Ingredient(name='Parsley',
                              category='flavouring')
    flavouring_7 = Ingredient(name='Soy sauce',
                              category='flavouring')

    db.session.add(flavouring_1)
    db.session.add(flavouring_2)
    db.session.add(flavouring_3)
    db.session.add(flavouring_4)
    db.session.add(flavouring_5)
    db.session.add(flavouring_6)
    db.session.add(flavouring_7)

    # CREATING COOKWARE
    cookware_1  = Cookware(name='Frying pan')
    cookware_2  = Cookware(name='Sous vide')
    cookware_3  = Cookware(name='Dutch oven')
    cookware_4  = Cookware(name='Air frier')
    cookware_5  = Cookware(name='Burner')
    cookware_6  = Cookware(name='Coffee brewer')
    cookware_7  = Cookware(name='Grill')
    cookware_8  = Cookware(name='Large pot')
    cookware_9  = Cookware(name='Microwave')
    cookware_10 = Cookware(name='Oven form')
    cookware_11 = Cookware(name='Tea kettle')
    db.session.add(cookware_1)
    db.session.add(cookware_2)
    db.session.add(cookware_3)
    db.session.add(cookware_4)
    db.session.add(cookware_5)
    db.session.add(cookware_6)
    db.session.add(cookware_7)
    db.session.add(cookware_8)
    db.session.add(cookware_9)
    db.session.add(cookware_10)
    db.session.add(cookware_11)

    # CREATING COOKING STYLES
    style_0 = Style(name='I don\u0027t prefer any style')
    style_1 = Style(name='Street food inspired')
    style_2 = Style(name='High end')
    style_3 = Style(name='Budget')
    style_4 = Style(name='Slow cooked')
    style_5 = Style(name='Sharing')
    db.session.add(style_0)
    db.session.add(style_1)
    db.session.add(style_2)
    db.session.add(style_3)
    db.session.add(style_4)
    db.session.add(style_5)

    #CREATING USERS
    hashed_password = bcrypt.generate_password_hash('testing').decode('utf-8')
    user_1 = User(username='Marcus',
                  email='default@test.com',
                  image_file='another_pic.jpeg',
                  password=hashed_password,
                  style=style_1,
                  user_intolerances=[carb_1, protein_1],
                  cookware=[cookware_1, cookware_2]
                  )
    db.session.add(user_1)

    hashed_password = bcrypt.generate_password_hash('testing2').decode('utf-8')
    user_2 = User(username='Karl IV',
                  email='second@test.com',
                  image_file='7798432669b8b3ac.jpg',
                  password=hashed_password,
                  style=style_1,
                  user_intolerances=[carb_1],
                  cookware=[cookware_1]
                  )
    db.session.add(user_2)

    hashed_password = bcrypt.generate_password_hash('testing3').decode('utf-8')
    user_3 = User(username='Karl XVI',
                  email='third@test.com',
                  password=hashed_password,
                  style=style_1,
                  user_intolerances=[carb_1, flavouring_1],
                  cookware=[cookware_2]
                  )
    db.session.add(user_3)

    #CREATING ADMINS
    hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
    admin_1 = User(username='Karl Lundqvist',
                    is_admin=True,
                    email='karl@tabl.io',
                    image_file='oogabooga.jpg',
                    password=hashed_password,
                    style=style_1,
                    user_intolerances=[carb_1, flavouring_1],
                    cookware=[cookware_2]
                    )

    hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
    admin_2 = User(username='Marcus Neidert',
                    is_admin=True,
                    email='marcus@tabl.io',
                    password=hashed_password,
                    style=style_2,
                    user_intolerances=[carb_1, flavouring_1],
                    cookware=[cookware_2]
                    )

    db.session.add(admin_1)
    db.session.add(admin_2)


    try:
        db.session.commit()
        print('\nFinalized - database created successfully!')
    except Exception as e:
        print('The operations were not successful. Error:', file=sys.stderr)
        print(e, file=sys.stderr)
        db.session.rollback()


if __name__ == '__main__':
    reload_database()
    print(User.query.all())
    categories = []

    for category in Ingredient.query.distinct(Ingredient.category).all():
        if category.category in categories:
            continue
        else:
            categories.append(category.category)