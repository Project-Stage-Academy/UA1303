# Generated by Django 4.2.16 on 2025-01-10 19:12

from django.db import migrations
from notifications.models import NotificationCategory

def add_notifications(apps, schema_editor):
    notification_categories = [
        NotificationCategory(name="follow", description="A new investor is following your startup."),
        NotificationCategory(name="update", description="A startup has updated its profile."),
        NotificationCategory(name="project", description="A startup has added a new project."),
    ]
    NotificationCategory.objects.bulk_create(notification_categories)

class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_startupnotification_and_more'),
    ]

    operations = [
         migrations.RunPython(add_notifications)
    ]
