# Generated by Django 5.2 on 2025-06-18 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dmad', '0013_alter_subjecttermname_subjectterm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gndsubjectcategory',
            name='link',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
