from django.db import migrations
from django.contrib.auth.hashers import make_password



users_data = [
    {
        "first_name": "Oleksii", 
        "last_name": "Shumylo",
        "email": "oleksii@shumylo.com",
        "title": "Python developer",
        "role": 3,
        "is_staff": True,
        "is_superuser": True,
        "password": "oleksiishumylo1303",
        "user_phone": "+3807773300"
    },
    {
        "first_name": "Vasyl",
        "last_name": "Yavorskyi",
        "email": "vasyl@yavorskyi.com",
        "title": "Python developer",
        "role": 3,
        "is_staff": True,
        "is_superuser": True,
        "password": "vasylyavorskyi1303",
        "user_phone": "+3807773310"
    },
    {
        "first_name": "Kyryl",
        "last_name": "Andrieiev",
        "email": "kyryl@andrieiev.com",
        "title": "Python developer",
        "role": 3,
        "is_staff": True,
        "is_superuser": True,
        "password": "kyrylandrieiev1303",
        "user_phone": "+3807773320"
    },
    {
        "first_name": "Iryna",
        "last_name": "Mladanovych",
        "email": "iryna@mladanovych.com",
        "title": "Python developer",
        "role": 3,
        "created_at": "",
        "is_staff": True,
        "is_superuser": True,
        "password": "irynamladanovych1303",
        "user_phone": "+3807773330"
    },
    {
        "first_name": "Dmytro",
        "last_name": "Kyrychuk",
        "email": "dmytro@kyrychuk.com",
        "title": "Python developer",
        "role": 3,
        "is_staff": True,
        "is_superuser": True,
        "password": "dmytrokyrychuk1303",
        "user_phone": "+3807773340"
    },
    {
        "first_name": "Serhii",
        "last_name": "Kryvosheiev",
        "email": "serhii@kryvosheiev.com",
        "title": "Python developer",
        "role": 3,
        "is_staff": True,
        "is_superuser": True,
        "password": "serhiikryvosheiev1303",
        "user_phone": "+3807773350"
    },
    {
        "first_name": "Maksym",
        "last_name": "Derkach",
        "email": "maksym@derkach.com",
        "title": "Python developer",
        "role": 3,
        "is_staff": True,
        "is_superuser": True,
        "password": "maksymderkach1303",
        "user_phone": "+3807773360"
    },
    {
        "first_name": "Bohdan",
        "last_name": "Forkutsa",
        "email": "bohdan@forkutsa.com",
        "title": "Python developer",
        "role": 3,
        "is_staff": True,
        "is_superuser": True,
        "password": "bohdanforkutsa1303",
        "user_phone": "+3807773370"
    },
    {
        "first_name": "Danyl",
        "last_name": "Koltak",
        "email": "danyl@koltak.com",
        "title": "Python developer",
        "role": 3,
        "is_staff": True,
        "is_superuser": True,
        "password": "danylkoltak1303",
        "user_phone": "+3807773380"
    },
    {
        "first_name": "Rebecca",
        "last_name": "Buck",
        "email": "mollylewis@simmons.info",
        "title": "Production designer",
        "role": 0,
        "is_staff": True,
        "is_superuser": False,
        "password": "f8b2d3a9p4w1",
        "user_phone": "+1234567890"
    },
    {
        "first_name": "Cindy",
        "last_name": "Miller",
        "email": "jacksonjeffery@moore.com",
        "title": "Financial trader",
        "role": 0,
        "is_staff": False,
        "is_superuser": False,
        "password": "b7v2q1w3p5z6",
        "user_phone": "+1234567891"
    },
    {
        "first_name": "Keith",
        "last_name": "Smith",
        "email": "urobinson@shaw.org",
        "title": "Materials engineer",
        "role": 1,
        "created_at": "",
        "is_staff": True,
        "is_superuser": False,
        "password": "t1r8j7l2l5o9",
        "user_phone": "+1234567892"
    },
    {
        "first_name": "Brenda",
        "last_name": "Hernandez",
        "email": "kthompson@reyes-hall.biz",
        "title": "Chief Operating Officer",
        "role": 1,
        "is_staff": False,
        "is_superuser": False,
        "password": "k5y8b1x3a6v2",
        "user_phone": "+1234567893"
    },
    {
        "first_name": "Morgan",
        "last_name": "Martinez",
        "email": "levysarah@payne.com",
        "title": "Child psychotherapist",
        "role": 2,
        "is_staff": True,
        "is_superuser": False,
        "password": "d3w2t7r2h9r9",
        "user_phone": "+314 589-7483"
    },
    {
        "first_name": "Kenneth",
        "last_name": "Russell",
        "email": "browndavid@hotmail.com",
        "title": "Newspaper journalist",
        "role": 2,
        "is_staff": False,
        "is_superuser": False,
        "password": "s9h4z3q7g1p5",
        "user_phone": "+44 7723 456789"
    },
]


def add_users(apps, schema_editor):
    CustomUser = apps.get_model('users', 'CustomUser')
    
    for user_data in users_data:
        user = CustomUser(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            user_phone=user_data["user_phone"],
            title=user_data["title"],
            role=user_data["role"],
            is_staff=user_data["is_staff"],
            is_superuser=user_data["is_superuser"],
        )
        user.password = make_password(user_data["password"])
        user.save()


def remove_users(apps, schema_editor):
    CustomUser = apps.get_model('users', 'CustomUser')

    for user_data in users_data:
        CustomUser.objects.filter(email=user_data["email"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_users, remove_users),
    ]
