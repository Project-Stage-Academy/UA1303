from django.db import migrations



startup_profiles_data = [
    {
        "user_email": "vasyl@yavorskyi.com",
        "company_name": "Harvest Bite Foods Inc.",
        "industry": "Organic Produce",
        "size": 540,
        "country": "USA",
        "city": "Denver",
        "zip_code": "80202",
        "address": "1245 Market Street",
        "phone": "+1 303-555-0181",
        "email": "contact@harvestbite.com",
        "description": "Pioneers in sustainable organic \
            produce distribution and innovation."
    },
    {
        "user_email": "iryna@mladanovych.com",
        "company_name": "Crimson Culinary Creations",
        "industry": "Gourmet Meals",
        "size": 280,
        "country": "Canada",
        "city": "Toronto",
        "zip_code": "M5G 1Z8",
        "address": "201 Bloor Street West",
        "phone": "+1 416-555-0192",
        "email": "info@crimsonculinary.com",
        "description": "Elevating everyday dining with exquisite, \
            chef-crafted gourmet meals."
    },
    {
        "user_email": "dmytro@kyrychuk.com",
        "company_name": "Blueberry Fields Co.",
        "industry": "Berry Farming",
        "size": 350,
        "country": "UK",
        "city": "Bristol",
        "zip_code": "BS1 6AU",
        "address": "45 Harbour Road",
        "phone": "+44 117-555-0167",
        "email": "support@blueberryfields.co.uk",
        "description": "Delivering the freshest berries from farm \
            to table across the UK."
    },
    {
        "user_email": "maksym@derkach.com",
        "company_name": "Golden Grain Enterprises",
        "industry": "Cereal Production",
        "size": 410,
        "country": "Australia",
        "city": "Sydney",
        "zip_code": "2000",
        "address": "101 Pitt Street",
        "phone": "+61 2-5551-0184",
        "email": "hello@goldengrain.com.au",
        "description": "Crafting wholesome breakfast options for a \
            healthy start to the day."
    },
    {
        "user_email": "bohdan@forkutsa.com",
        "company_name": "Seaside Snacks Ltd.",
        "industry": "Seafood Snacks",
        "size": 220,
        "country": "New Zealand",
        "city": "Auckland",
        "zip_code": "1010",
        "address": "22 Queen Street",
        "phone": "+64 9-555-0145",
        "email": "orders@seasidesnacks.co.nz",
        "description": "Bringing the ocean's finest to your pantry \
            with savory seafood treats."
    },
    {
        "user_email": "urobinson@shaw.org",
        "company_name": "Meadow Delight Creamery",
        "industry": "Dairy Products",
        "size": 610,
        "country": "Ireland",
        "city": "Dublin",
        "zip_code": "D02 W820",
        "address": "7 St. Stephen's Green",
        "phone": "+353 1-555-0178",
        "email": "sales@meadowdelight.ie",
        "description": "Traditional Irish dairy products, made with \
            love and care."
    },
    {
        "user_email": "kthompson@reyes-hall.biz",
        "company_name": "Savory Soups & Broths Co.",
        "industry": "Packaged Foods",
        "size": 390,
        "country": "USA",
        "city": "Seattle",
        "zip_code": "98101",
        "address": "725 Pine Street",
        "phone": "+1 206-555-0193",
        "email": "admin@savorysoups.com",
        "description": "A warm bowl of comfort, crafted with premium \
            ingredients."
    },
    {
        "user_email": "kyryl@andrieiev.com",
        "company_name": "Tropical Flavors Exports",
        "industry": "Fruit Processing",
        "size": 475,
        "country": "Brazil",
        "city": "Rio de Janeiro",
        "zip_code": "20031-007",
        "address": "50 Rua da Quitanda",
        "phone": "+55 21-555-0186",
        "email": "team@tropicalflavors.com.br",
        "description": "Exporting the vibrant flavors of Brazil's \
            finest tropical fruits."
    },
    {
        "user_email": "serhii@kryvosheiev.com",
        "company_name": "Mountain Harvest Beverages",
        "industry": "Specialty Drinks",
        "size": 320,
        "country": "Switzerland",
        "city": "Zurich",
        "zip_code": "8001",
        "address": "99 Bahnhofstrasse",
        "phone": "+41 44-555-0123",
        "email": "queries@mountainharvest.ch",
        "description": "Crafting refreshing beverages inspired by \
            the Swiss Alps."
    },
    {
        "user_email": "oleksii@shumilo.com",
        "company_name": "Emerald Bites Catering",
        "industry": "Catering Services",
        "size": 290,
        "country": "South Africa",
        "city": "Cape Town",
        "zip_code": "8001",
        "address": "33 Long Street",
        "phone": "+27 21-555-0179",
        "email": "bookings@emeraldbites.co.za",
        "description": "Catering fresh, elegant meals for events \
            of all sizes."
    },
]


def add_startup_profiles(apps, schema_editor):
    StartupProfile = apps.get_model('profiles', 'StartupProfile')
    CustomUser = apps.get_model('users', 'CustomUser')

    for startup_profile_data in startup_profiles_data:
        user = CustomUser.objects.get(email=startup_profile_data["user_email"])
        StartupProfile.objects.create(
            user=user,
            company_name=startup_profile_data["company_name"],
            industry=startup_profile_data["industry"],
            size=startup_profile_data["size"],
            country=startup_profile_data["country"],
            city=startup_profile_data["city"],
            zip_code=startup_profile_data["zip_code"],
            address=startup_profile_data["address"],
            phone=startup_profile_data["phone"],
            email=startup_profile_data["email"],
            description=startup_profile_data["description"],
        )


def remove_startup_profiles(apps, schema_editor):
    StartupProfile = apps.get_model('profiles', 'StartupProfile')

    for startup_profile_data in startup_profiles_data:
        StartupProfile.objects.get(
            email=startup_profile_data["email"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
        ('users', '0002_add_users'),
    ]

    operations = [
        migrations.RunPython(add_startup_profiles, remove_startup_profiles),
    ]
