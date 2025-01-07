from django.db import migrations



investor_profiles_data = [
    {
        "user_email": "levysarah@payne.com",
        "country": "US",
        "city": "St. Louis",
        "zip_code": "63101",
        "address": "1428 Market St",
        "phone": "+314 589-7483",
        "email": "levysarah@payne.com",
        "account_balance": 12323.44,
    },
    {
        "user_email": "oleksii@shumylo.com",
        "country": "UA",
        "city": "Lviv",
        "zip_code": "79018",
        "address": "57 Fedkovycha Street",
        "phone": "+380 67 123 4567",
        "email": "oleksii@shumylo.com",
        "account_balance": 54628.80,
    },
    {
        "user_email": "browndavid@hotmail.com",
        "country": "GB",
        "city": "London",
        "zip_code": "W1U 8EW",
        "address": "25 Baker Street",
        "phone": "+44 7723 456789",
        "email": "browndavid@hotmail.com",
        "account_balance": 99212.4,
    },
    {
        "user_email": "bohdan@forkutsa.com",
        "country": "UA",
        "city": "Lviv",
        "zip_code": "79018",
        "address": "57 Fedkovycha Street",
        "phone": "+380 50 987 6543",
        "email": "bohdan@forkutsa.com",
        "account_balance": 1243320.9,
    },
    {
        "user_email": "danyl@koltak.com",
        "country": "UA",
        "city": "Dnipro",
        "zip_code": "49000",
        "address": "22 Dmytro Yavornytsky Avenue",
        "phone": "+380 99 654 3210",
        "email": "danyl@koltak.com",
        "account_balance": 213432.77,
    },
    {
        "user_email": "maksym@derkach.com",
        "country": "UA",
        "city": "Kyiv",
        "zip_code": "02230",
        "address": "3A Mykhaila Hryshka Street",
        "phone": "+380 68 234 5678",
        "email": "maksym@derkach.com",
        "account_balance": 232032.9,
    },
    {
        "user_email": "serhii@kryvosheiev.com",
        "country": "UA",
        "city": "Kyiv",
        "zip_code": "02230",
        "address": "3A Mykhaila Hryshka Street",
        "phone": "+380 63 876 5432",
        "email": "serhii@kryvosheiev.com",
        "account_balance": 12373.63,
    },
    {
        "user_email": "iryna@mladanovych.com",
        "country": "UA",
        "city": "Dnipro",
        "zip_code": "49000",
        "address": "22 Dmytro Yavornytsky Avenue",
        "phone": "+380 66 432 1098",
        "email": "iryna@mlad anovych.com",
        "account_balance": 473812.4,
    },
    {
        "user_email": "vasyl@yavorskyi.com",
        "country": "UA",
        "city": "Lviv",
        "zip_code": "79018",
        "address": "57 Fedkovycha Street",
        "phone": "+380 95 678 9012",
        "email": "vasyl@yavorskyi.com",
        "account_balance": 45.99,
    },
    {
        "user_email": "dmytro@kyrychuk.com",
        "country": "UA",
        "city": "Kharkiv",
        "zip_code": "61057",
        "address": "10 Sumska Street",
        "phone": "+380 96 345 6789",
        "email": "dmytro@kyrychuk.com",
        "account_balance": 123422.3,
    },
]


def add_investor_profiles(apps, schema_editor):
    InvestorProfile = apps.get_model('profiles', 'InvestorProfile')
    CustomUser = apps.get_model('users', 'CustomUser')

    for investor_profile_data in investor_profiles_data:
        user = CustomUser.objects.get(email=investor_profile_data["user_email"])
        InvestorProfile.objects.create(
            user=user,
            country=investor_profile_data["country"],
            city=investor_profile_data["city"],
            zip_code=investor_profile_data["zip_code"],
            address=investor_profile_data["address"],
            phone=investor_profile_data["phone"],
            email=investor_profile_data["email"],
            account_balance=investor_profile_data["account_balance"],
        )


def remove_investor_profiles(apps, schema_editor):
    InvestorProfile = apps.get_model('profiles', 'InvestorProfile')

    for investor_profile_data in investor_profiles_data:
        InvestorProfile.objects.get(
            email=investor_profile_data["email"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
        ('users', '0002_add_users'),
        ('profiles', '0002_add_startup_profiles'),
    ]

    operations = [
        migrations.RunPython(add_investor_profiles, remove_investor_profiles),
    ]
