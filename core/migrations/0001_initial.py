# Generated by Django 3.1.1 on 2020-09-24 00:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_name', models.CharField(max_length=30)),
                ('lesson_code', models.TextField(max_length=750)),
            ],
        ),
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concept_key', models.CharField(max_length=30)),
                ('concept_text', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('headline', models.CharField(default='Try Again!', max_length=50)),
                ('feedback_type', models.CharField(choices=[('DEF', 'Default'), ('COR', 'Correct'), ('SIM', 'Simplify'), ('SELF', 'Self Reference'), ('NUM', 'Used Concrete Value as Answer'), ('INIT', 'Missing # Symbol'), ('ALG', 'Algebra'), ('VAR', 'Variable'), ('SUB', 'Sub_Lesson')], default='DEF', max_length=4)),
                ('feedback_text', models.TextField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Incorrect_Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lesson_text', models.CharField(default='Lesson2', max_length=200)),
                ('answer_type', models.CharField(choices=[('SIM', 'Simplify'), ('SELF', 'Self Reference'), ('NUM', 'Used Concrete Value as Answer'), ('INIT', 'Missing # Symbol'), ('ALG', 'Algebra'), ('VAR', 'Variable')], default='SIM', max_length=4)),
                ('answer_text', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lesson_name', models.CharField(max_length=50)),
                ('lesson_title', models.CharField(default='default', max_length=50)),
                ('instruction', models.TextField(default='Please complete the Confirm assertion(s) and check correctness.')),
                ('number_of_attempts', models.IntegerField(default=100)),
                ('correct', models.CharField(default='Lesson To Go To', max_length=50)),
                ('sub_lessons_available', models.BooleanField(default=False)),
                ('simplify', models.CharField(default='None', max_length=50)),
                ('self_reference', models.CharField(default='None', max_length=50)),
                ('use_of_concrete_values', models.CharField(default='None', max_length=50)),
                ('not_using_initial_value', models.CharField(default='None', max_length=50)),
                ('algebra', models.CharField(default='None', max_length=50)),
                ('variable', models.CharField(default='None', max_length=50)),
                ('screen_record', models.BooleanField()),
                ('code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.code')),
                ('feedback', models.ManyToManyField(blank=True, to='core.Feedback')),
                ('incorrect_answers', models.ManyToManyField(blank=True, to='core.Incorrect_Answer')),
                ('lesson_concept', models.ManyToManyField(blank=True, to='core.Concept')),
            ],
        ),
        migrations.CreateModel(
            name='McChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice_text', models.TextField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_key', models.CharField(max_length=30)),
                ('reference_text', models.TextField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Reasoning',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reasoning_name', models.CharField(max_length=30)),
                ('reason_occurrence', models.CharField(choices=[('START', 'Start'), ('NONE', 'None'), ('SIM', 'Simplify'), ('SELF', 'Self Reference'), ('NUM', 'Used Concrete Value as Answer'), ('INIT', 'Missing # Symbol'), ('ALG', 'Algebra'), ('VAR', 'Variable')], default='NONE', max_length=5)),
                ('reasoning_type', models.CharField(choices=[('MC', 'Multiple Choice'), ('Text', 'Free Response'), ('Both', 'Multiple Choice and Free Response'), ('None', 'None')], default='None', max_length=4)),
                ('mc_set', models.ManyToManyField(blank=True, to='core.McChoice')),
                ('reasoning_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.question')),
            ],
        ),
        migrations.AddField(
            model_name='mcchoice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.question'),
        ),
        migrations.CreateModel(
            name='LessonSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('set_name', models.CharField(max_length=50)),
                ('set_description', models.TextField(default='This set is designed to further your understanding')),
                ('lessons', models.ManyToManyField(blank=True, to='core.Lesson')),
            ],
        ),
        migrations.AddField(
            model_name='lesson',
            name='reason',
            field=models.ManyToManyField(blank=True, to='core.Reasoning'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='reference_set',
            field=models.ManyToManyField(blank=True, to='core.Reference'),
        ),
    ]
