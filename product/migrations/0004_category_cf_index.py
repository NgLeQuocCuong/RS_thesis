# Generated by Django 3.1.2 on 2021-05-07 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_category_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='cf_index',
            field=models.IntegerField(default=-1),
        ),
    ]
