from django.db import migrations
from django.db.models import F
from profiles.models import InvestorProfile, StartupProfile
from notifications.models import NotificationType, StartUpNotification

def add_notifications(apps, schema_editor):
    notification_types = [
        NotificationType(name="follow", description="A new investor is following your startup."),
        NotificationType(name="update", description="A startup has updated its profile."),
        NotificationType(name="project", description="A startup has added a new project."),
    ]
    NotificationType.objects.bulk_create(notification_types)


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_notifications),
    ]