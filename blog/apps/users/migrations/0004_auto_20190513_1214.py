# Generated by Django 2.2.1 on 2019-05-13 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=100),
        ),
    ]
