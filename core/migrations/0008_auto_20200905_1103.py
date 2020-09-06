# Generated by Django 3.1.1 on 2020-09-05 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_remove_lesson_syntax'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='variable_answers',
            field=models.ManyToManyField(blank=True, related_name='variable_answers', to='core.Incorrect_Answer'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='simplify_answers',
            field=models.ManyToManyField(blank=True, related_name='simplify_answers', to='core.Incorrect_Answer'),
        ),
    ]
