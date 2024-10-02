# Generated by Django 5.1.1 on 2024-09-25 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0008_rename_bidding_bid_alter_listing_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="bid",
            options={"ordering": ["created_at"]},
        ),
        migrations.AddField(
            model_name="listing",
            name="start_price",
            field=models.FloatField(default=0),
        ),
    ]
