# Generated by Django 5.1.4 on 2025-05-21 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edwoca', '0004_remove_expression_expressions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='expression',
            name='comment',
            field=models.TextField(null=True),
        ),
    ]
