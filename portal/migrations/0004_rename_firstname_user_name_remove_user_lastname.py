# Generated by Django 4.2.4 on 2023-08-24 05:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0003_alter_user_email_alter_user_firstname_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="firstname",
            new_name="name",
        ),
        migrations.RemoveField(
            model_name="user",
            name="lastname",
        ),
    ]
