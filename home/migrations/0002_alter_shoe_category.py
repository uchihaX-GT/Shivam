# Generated by Django 4.2.7 on 2024-03-08 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoe',
            name='category',
            field=models.CharField(choices=[('MENS', 'Mens'), ('WOMENS', 'Womens')], max_length=20),
        ),
    ]
