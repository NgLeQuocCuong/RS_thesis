# Generated by Django 3.1.2 on 2021-04-04 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_remove_category_fake_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='code',
            field=models.IntegerField(default=-1),
        ),
    ]