from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Outlet",
            fields=[
                ("outlet_code", models.CharField(max_length=16,
                                                 primary_key=True,
                                                 serialize=False)),
                ("outlet_name", models.CharField(max_length=120)),
                ("route_code", models.CharField(blank=True, max_length=16)),
            ],
            options={"ordering": ["outlet_code"]},
        ),
    ]
