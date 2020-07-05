# Generated by Django 3.0.7 on 2020-07-02 14:47

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_nickname', models.CharField(max_length=25, validators=[django.core.validators.MinLengthValidator(1)], verbose_name='Nickname')),
                ('user_school', models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(1)], verbose_name='School')),
                ('user_class', models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(1)], verbose_name='Class')),
                ('user_gender', models.CharField(max_length=50, validators=[django.core.validators.MinLengthValidator(1)], verbose_name='Gender')),
                ('user_race', models.CharField(max_length=50, validators=[django.core.validators.MinLengthValidator(1)], verbose_name='Race')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
