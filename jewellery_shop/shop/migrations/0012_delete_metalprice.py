from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_product_is_new_arrival'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MetalPrice',
        ),
    ]
