# Generated by Django 4.2.1 on 2023-06-01 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_samplebio_sampleprofileimage_starteduser_credit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='image_profile',
            field=models.ImageField(null=True, upload_to='account/profiles'),
        ),
        migrations.AlterField(
            model_name='account',
            name='session_file',
            field=models.FileField(null=True, upload_to='sessions'),
        ),
        migrations.AlterField(
            model_name='account',
            name='session_string',
            field=models.TextField(null=True),
        ),
    ]
