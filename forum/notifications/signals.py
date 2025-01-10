from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import StartUpNotification, NotificationType
from profiles.models import InvestorProfile, StartupProfile
from .serializers import StartUpNotificationCreateSerializer

@receiver(m2m_changed, sender=StartupProfile.followers.through)
def create_startup_notification(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set:
            investor = InvestorProfile.objects.get(pk=pk)
            notification_type = NotificationType.objects.get(name='follow')
            data = {
                'notification_type': notification_type.id,
                'investor': investor.id,
                'startup': instance.id,
            }
            serializer = StartUpNotificationCreateSerializer(data=data)
            if serializer.is_valid():
                serializer.save()

                serializer = StartUpNotificationCreateSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
            else:
                print(serializer.errors)