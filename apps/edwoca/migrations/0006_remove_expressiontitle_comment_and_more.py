# Generated by Django 5.1.4 on 2025-05-27 14:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edwoca', '0005_expression_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expressiontitle',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='expressiontitle',
            name='gnd_id',
        ),
        migrations.RemoveField(
            model_name='expressiontitle',
            name='history',
        ),
    ]
