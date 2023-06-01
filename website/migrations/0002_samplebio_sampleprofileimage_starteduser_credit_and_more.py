# Generated by Django 4.2.1 on 2023-06-01 09:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SampleBio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SampleProfileImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_profile', models.ImageField(upload_to='sample/profiles')),
            ],
        ),
        migrations.AddField(
            model_name='starteduser',
            name='credit',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=15)),
                ('session_string', models.TextField()),
                ('is_logged_in', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('bio', models.TextField(blank=True, null=True)),
                ('image_profile', models.ImageField(upload_to='account/profiles')),
                ('session_file', models.FileField(upload_to='sessions')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='website.starteduser')),
            ],
        ),
    ]
