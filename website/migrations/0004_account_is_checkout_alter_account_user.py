# Generated by Django 4.2.1 on 2023-06-04 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_alter_account_image_profile_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_checkout',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='account',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accounts', to='website.starteduser'),
        ),
    ]
