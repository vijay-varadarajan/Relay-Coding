# Generated by Django 4.2.4 on 2023-08-23 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0002_alter_user_options_alter_user_managers_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="firstname",
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name="user",
            name="lastname",
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name="user",
            name="password",
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
