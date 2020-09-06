# Generated by Django 3.1.1 on 2020-09-05 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20200905_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='algebra',
            field=models.CharField(default='None', max_length=50),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='not_using_initial_value',
            field=models.CharField(default='None', max_length=50),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='reason',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.reasoning'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='self_reference',
            field=models.CharField(default='None', max_length=50),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='simplify',
            field=models.CharField(default='None', max_length=50),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='use_of_concrete_values',
            field=models.CharField(default='None', max_length=50),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='variable',
            field=models.CharField(default='None', max_length=50),
        ),
    ]
