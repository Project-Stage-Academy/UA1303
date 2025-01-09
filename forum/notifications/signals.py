from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import StartUpNotification, NotificationType
from profiles.models import InvestorProfile, StartupProfile

@receiver(m2m_changed, sender=StartupProfile.followers.through)
def create_startup_notification(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set:
            investor = InvestorProfile.objects.get(pk=pk)
            notification_type, _ = NotificationType.objects.get_or_create(name='New Follower')
            StartUpNotification.objects.create(
                notification_type=notification_type,
                investor=investor,
                startup=instance
            )