# Generated by Django 2.0.7 on 2018-10-04 10:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0006_auto_20181004_1805'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-comment_time']},
        ),
    ]