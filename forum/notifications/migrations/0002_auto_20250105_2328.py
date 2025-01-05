from django.db import migrations
from django.db.models import F
from profiles.models import InvestorProfile, StartupProfile
from notifications.models import NotificationType, StartUpNotification

def add_notifications(apps, schema_editor):
    # Get the notification type
    notification_type, _ = NotificationType.objects.get_or_create(name='New investor follows you')

    # Get the startup
    startup = StartupProfile.objects.get(id=10)

    # Create notifications for investors 1-5
    for investor_id in range(1, 6):
        investor = InvestorProfile.objects.get(id=investor_id)
        StartUpNotification.objects.get_or_create(
            notification_type=notification_type,
            investor=investor,
            startup=startup,
            is_read=False,
        )

class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_notifications),
    ]