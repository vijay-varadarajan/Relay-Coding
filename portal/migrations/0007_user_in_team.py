# Generated by Django 4.2.4 on 2023-08-24 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0006_alter_team_team_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="in_team",
            field=models.BooleanField(default=False),
        ),
    ]
