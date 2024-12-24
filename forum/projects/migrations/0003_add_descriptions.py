from django.db import migrations



descriptions_data = [
    {
        "project_title": "Meat Eater",
        "description":
            (
                "Meat Eater is a bold startup catering to meat "
                "lovers with a focus on high-quality, ethically sourced "
                "meats. Specializing in grass-fed, free-range, and "
                "hormone-free options, Meat Eater delivers premium "
                "cuts directly to your door. Committed to "
                "sustainability, it strives to reduce the environmental "
                "impact of meat production while ensuring exceptional "
                "taste and nutrition."
            ),
        "created_at": "2019-04-12 08:32:46",
    },
    {
        "project_title": "Vegan Shop",
        "description": 
            (
                "Vegan Shop is a dedicated marketplace for plant-based "
                "products, offering a wide range of vegan groceries, "
                "snacks, and household items. Focused on promoting a "
                "cruelty-free lifestyle, Vegan Shop connects consumers "
                "with top-quality, sustainable, and eco-friendly "
                "products. From fresh produce to vegan essentials, "
                "it’s your one-stop shop for all things plant-based."
            ),
        "created_at": "2021-01-29 21:17:53",
    },
    {
        "project_title": "EatIt",
        "description": 
            (
                "EatIt is a fun, innovative startup that makes healthy "
                "eating simple and enjoyable. With a focus on "
                "delicious, balanced meals, EatIt offers customizable "
                "meal plans tailored to fit various dietary needs. "
                "Whether for weight management or maintaining a healthy "
                "lifestyle, EatIt brings convenience, flavor, and "
                "nutrition together in every bite."
            ),
        "created_at": "2017-10-06 10:25:03",
    },
    {
        "project_title": "Easy Eat",
        "description":
            (
                "Easy Eat is a convenience-driven startup "
                "revolutionizing mealtime with quick, nutritious "
                "options. Offering a wide variety of ready-to-heat "
                "meals, Easy Eat makes healthy eating effortless for "
                "busy individuals and families. With a focus on taste, "
                "freshness, and quality, it ensures that everyone can "
                "enjoy wholesome, satisfying meals without the stress "
                "of cooking."
            ),
        "created_at": "2021-02-15 17:04:38",
    },
    {
        "project_title": "Mega Meal",
        "description":
            (
                "Mega Meal is an innovative food delivery startup "
                "offering a wide range of ready-to-eat meals designed "
                "for busy professionals and families. With a focus on "
                "convenience and variety, Mega Meal serves healthy, "
                "chef-prepared dishes made from locally sourced ingredients. "
                "It aims to make nutritious eating easy, affordable, "
                "and accessible to everyone."
            ),
        "created_at": "2020-03-24 14:59:12",
    },
    {
        "project_title": "Green Bite",
        "description":
            (
                "Green Bite is a sustainable food tech startup "
                "revolutionizing the way we eat. Focused on eco-friendly "
                "practices, it offers plant-based meal options made "
                "from locally sourced ingredients. With a mission to "
                "reduce food waste and carbon footprints, Green Bite "
                "combines innovation with taste to deliver healthy, "
                "environmentally conscious dining solutions."
            ),
        "created_at": "2020-06-03 17:25:15",
    },
    {
        "project_title": "Taste Tech",
        "description":
            (
                "Taste Tech is a cutting-edge startup blending "
                "technology and flavor innovation. Specializing in "
                "AI-driven food personalization, it creates tailored "
                "recipes and smart kitchen solutions. From advanced "
                "flavor profiles to automated cooking tools, Taste "
                "Tech is redefining the food experience with a "
                "focus on convenience, quality, and culinary creativity."
            ),
        "created_at": "2021-04-15 09:10:42",
    },
    {
        "project_title": "Eco Eats",
        "description":
            (
                "Eco Eats is a sustainability-focused startup "
                "connecting eco-conscious consumers with local, "
                "organic food providers. Through its innovative app, "
                "users can discover surplus meals, reduce food waste, "
                "and support sustainable farming practices. Eco Eats "
                "is committed to promoting affordability, environmental "
                "impact, and a healthier planet one meal at a time."
            ),
        "created_at": "2023-13-29 18:40:57",
    },
    {
        "project_title": "Farm Fusion",
        "description":
            (
                "Farm Fusion bridges the gap between local farms "
                "and modern kitchens. This innovative startup delivers "
                "fresh, organic produce directly from farmers to "
                "consumers, paired with curated recipes for effortless "
                "meal preparation. Combining sustainability with "
                "convenience, Farm Fusion empowers healthier eating "
                "while supporting small-scale agriculture and "
                "reducing food miles."
            ),
        "created_at": "2023-07-12 10:05:29",
    },
    {
        "project_title": "Food Flow",
        "description":
            (
                "Food Flow is a logistics-driven startup "
                "optimizing the journey of food from farm to table. "
                "With smart supply chain solutions, it ensures fresh, "
                "high-quality products reach consumers and businesses "
                "faster. Focused on reducing waste and enhancing "
                "efficiency, Food Flow streamlines operations for "
                "farmers, suppliers, and retailers, promoting a "
                "sustainable food ecosystem."
            ),
        "created_at": "2020-05-21 22:42:11",
    },
    {
        "project_title": "Meadow Project",
        "description":
            (
                "Meadow Project is a visionary startup dedicated "
                "to regenerating ecosystems through sustainable "
                "agriculture. By integrating technology with "
                "nature, it supports local farmers in cultivating "
                "organic, biodiversity-friendly produce. Meadow "
                "Project champions soil health, carbon sequestration, "
                "and community-driven food systems to create a "
                "greener, healthier future for all."
            ),
        "created_at": "2021-11-22 05:18:56",
    },
    {
        "project_title": "Nutri Nova",
        "description":
            (
                "Nutri Nova is a health-focused startup redefining "
                "nutrition through science and innovation. "
                "Specializing in personalized meal plans and "
                "functional foods, it uses advanced analytics to "
                "meet individual dietary needs. With a commitment "
                "to wellness and sustainability, Nutri Nova empowers "
                "healthier lifestyles through nutrient-rich, "
                "eco-friendly solutions."
            ),
        "created_at": "2022-03-10 14:33:03",
    },
    {
        "project_title": "Tropical Meal",
        "description":
            (
                "Tropical Meal brings the vibrant flavors of "
                "the tropics to your table. This unique startup offers "
                "ready-to-eat meals and ingredient kits inspired by "
                "tropical cuisines, made with sustainably sourced, "
                "exotic ingredients. Focused on convenience and "
                "authenticity, Tropical Meal transforms everyday "
                "dining into a flavorful escape to paradise."
            ),
        "created_at": "2022-12-05 20:14:44",
    },
    {
        "project_title": "Fresh Track",
        "description":
            (
                "Fresh Track is a forward-thinking startup revolutionizing "
                "the way fresh food reaches consumers. By utilizing "
                "advanced tracking technology, it ensures the quickest, "
                "most efficient delivery of farm-fresh produce, "
                "preserving quality and taste. Fresh Track connects "
                "consumers with local growers, promoting transparency "
                "and sustainability in the food supply chain."
            ),
        "created_at": "2024-03-19 06:57:37",
    },
    {
        "project_title": "Plant Power",
        "description":
            (
                "Plant Power is a dynamic startup dedicated to promoting "
                "plant-based nutrition for a healthier planet. Offering "
                "a range of delicious, nutrient-packed meals and snacks, "
                "it aims to make plant-based eating accessible and "
                "enjoyable for all. With a focus on sustainability and "
                "wellness, Plant Power is fueling a movement towards "
                "conscious, eco-friendly eating."
            ),
        "created_at": "2021-08-09 14:46:25",
    },
]


def add_descriptions(apps, schemaeditor):
    Project = apps.get_model('projects', 'Project')
    Description = apps.get_model('projects', 'Description')

    for description_data in descriptions_data:
        project = Project.objects.get(title=description_data["project_title"])
        Description.objects.create(
            project=project,
            description=description_data["description"],
            created_at=description_data["created_at"],
        )


def remove_descriptions(apps, schemaeditor):
    Project = apps.get_model('projects', 'Project')
    Description = apps.get_model('projects', 'Description')

    for description_data in descriptions_data:
        project = Project.objects.get(title=description_data["project_title"])
        Description.objects.get(project=project).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_add_projects'),
    ]

    operations = [
        migrations.RunPython(add_descriptions, remove_descriptions)
    ]