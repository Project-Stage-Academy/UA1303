# Generated by Django 4.2.16 on 2025-01-11 11:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_startupprofile_is_public'),
        ('notifications', '0004_add_notifications'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestorNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_read', models.BooleanField(db_index=True, default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investor_notifications', to='profiles.investorprofile')),
                ('notification_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investor_notifications', to='notifications.notificationcategory')),
                ('startup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investor_notifications', to='profiles.startupprofile')),
            ],
            options={
                'verbose_name': 'Investor Notification',
                'verbose_name_plural': 'Investor Notifications',
                'ordering': ['id'],
            },
        ),
    ]
