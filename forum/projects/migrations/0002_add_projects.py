from django.db import migrations



projects_data = [
    {
        "startup_email": "contact@harvestbite.com",
        "title": "Green Bite",
        "funding_goal": 11000,
        "is_published": False,
        "is_completed": False,
        "created_at": "2020-06-02 16:25:15",
    },
    {
        "startup_email": "info@crimsonculinary.com",
        "title": "Taste Tech",
        "funding_goal": 230000,
        "is_published": True,
        "is_completed": False,
        "created_at": "2021-03-15 09:14:42",
    },
    {
        "startup_email": "support@blueberryfields.co.uk",
        "title": "Eco Eats",
        "funding_goal": 250000,
        "is_published": False,
        "is_completed": False,
        "created_at": "2023-11-29 18:39:57",
    },
    {
        "startup_email": "hello@goldengrain.com.au",
        "title": "Farm Fusion",
        "funding_goal": 30000,
        "is_published": True,
        "is_completed": False,
        "created_at": "2023-07-04 12:05:29",
    },
    {
        "startup_email": "orders@seasidesnacks.co.nz",
        "title": "Food Flow",
        "funding_goal": 22000,
        "is_published": False,
        "is_completed": False,
        "created_at": "2020-05-18 23:42:11",
    },
    {
        "startup_email": "sales@meadowdelight.ie",
        "title": "Meadow Project",
        "funding_goal": 79900,
        "is_published": True,
        "is_completed": False,
        "created_at": "2021-10-22 07:18:56",
    },
    {
        "startup_email": "admin@savorysoups.com",
        "title": "Nutri Nova",
        "funding_goal": 85400,
        "is_published": False,
        "is_completed": False,
        "created_at": "2022-02-10 15:33:03",
    },
    {
        "startup_email": "team@tropicalflavors.com.br",
        "title": "Tropical Meal",
        "funding_goal": 1200000,
        "is_published": True,
        "is_completed": False,
        "created_at": "2022-12-04 20:10:44",
    },
    {
        "startup_email": "queries@mountainharvest.ch",
        "title": "Fresh Track",
        "funding_goal": 65000,
        "is_published": False,
        "is_completed": False,
        "created_at": "2024-01-19 06:52:37",
    },
    {
        "startup_email": "bookings@emeraldbites.co.za",
        "title": "Plant Power",
        "funding_goal": 42000,
        "is_published": True,
        "is_completed": False,
        "created_at": "2021-08-08 14:47:25",
    },
    {
        "startup_email": "bookings@emeraldbites.co.za",
        "title": "Mega Meal",
        "funding_goal": 67000,
        "is_published": False,
        "is_completed": True,
        "created_at": "2020-03-22 14:59:12",
    },
    {
        "startup_email": "queries@mountainharvest.ch",
        "title": "Easy Eat",
        "funding_goal": 225000,
        "is_published": False,
        "is_completed": True,
        "created_at": "2021-01-15 17:04:38",
    },
    {
        "startup_email": "team@tropicalflavors.com.br",
        "title": "EatIt",
        "funding_goal": 33003,
        "is_published": False,
        "is_completed": True,
        "created_at": "2017-09-06 10:25:03",
    },
    {
        "startup_email": "orders@seasidesnacks.co.nz",
        "title": "Vegan Shop",
        "funding_goal": 35500,
        "is_published": False,
        "is_completed": True,
        "created_at": "2020-12-29 21:17:53",
    },
    {
        "startup_email": "sales@meadowdelight.ie",
        "title": "Meat Eater",
        "funding_goal": 4000,
        "is_published": False,
        "is_completed": True,
        "created_at": "2019-04-11 08:32:46",
    },
]


def add_projects_data(apps, schemaeditor):
    StartupProfile = apps.get_model('profiles', 'StartupProfile')
    Project = apps.get_model('projects', 'Project')

    for project_data in projects_data:
        startup = StartupProfile.objects.get(email=project_data["startup_email"])
        Project.objects.create(
            startup=startup,
            title=project_data["title"],
            funding_goal=project_data["funding_goal"],
            is_published=project_data["is_published"],
            is_completed=project_data["is_completed"],
            created_at=project_data["created_at"],
        )


def remove_projects_data(apps, schemaeditor):
    Project = apps.get_model('projects', 'Project')
    StartupProfile = apps.get_model('profiles', 'StartupProfile')

    for project_data in projects_data:
        startup = StartupProfile.objects.get(email=project_data["startup_email"])
        Project.objects.filter(startup=startup).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
        ('profiles', '0003_add_startup_profiles'),
    ]

    operations = [
        migrations.RunPython(add_projects_data, remove_projects_data)
    ]