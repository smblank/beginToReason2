# Generated by Django 3.1.8 on 2021-05-09 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='correct_key',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.lesson'),
        ),
    ]
