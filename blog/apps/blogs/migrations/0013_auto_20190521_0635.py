# Generated by Django 2.2.1 on 2019-05-21 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0008_auto_20190516_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='image_url',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='image',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
