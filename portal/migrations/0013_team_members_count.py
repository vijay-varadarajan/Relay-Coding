# Generated by Django 4.1.7 on 2023-08-25 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0012_remove_team_member1_remove_team_member2_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="members_count",
            field=models.IntegerField(default=1),
        ),
    ]
