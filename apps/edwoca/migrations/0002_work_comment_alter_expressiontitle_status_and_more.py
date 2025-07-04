# Generated by Django 5.1.4 on 2025-04-29 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edwoca', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='comment',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='expressiontitle',
            name='status',
            field=models.CharField(choices=[('P', 'Primary'), ('A', 'Alternative'), ('T', 'Temporary')], default='P', max_length=1),
        ),
        migrations.AlterField(
            model_name='worktitle',
            name='status',
            field=models.CharField(choices=[('P', 'Primary'), ('A', 'Alternative'), ('T', 'Temporary')], default='P', max_length=1),
        ),
    ]
