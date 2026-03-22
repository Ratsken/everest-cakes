import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="herosection",
            name="linked_category",
            field=models.ForeignKey(
                blank=True,
                help_text="Associate this hero slide with a category (auto-fills CTA link & price badge)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="hero_sections",
                to="products.category",
            ),
        ),
    ]
