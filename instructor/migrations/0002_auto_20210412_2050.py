# Generated by Django 3.1.8 on 2021-04-13 00:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instructor', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='class',
            old_name='user_class',
            new_name='class_name',
        ),
    ]
