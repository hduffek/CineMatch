# Generated by Django 4.2.1 on 2023-06-22 21:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CineMatch', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Choice',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
    ]
