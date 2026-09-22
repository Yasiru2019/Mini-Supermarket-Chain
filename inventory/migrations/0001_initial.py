import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=50, unique=True)),
                ('barcode', models.CharField(blank=True, help_text='Barcode for a single base unit (e.g. one piece). Leave blank if it has none of its own.', max_length=50, null=True, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('unit_of_measure', models.CharField(choices=[('each', 'Each'), ('kg', 'Kilogram'), ('g', 'Gram'), ('l', 'Litre'), ('ml', 'Millilitre'), ('pack', 'Pack'), ('box', 'Box')], default='each', max_length=10)),
                ('cost_price', models.DecimalField(decimal_places=2, default=0, help_text='Cost for one base unit (e.g. one piece).', max_digits=10)),
                ('sell_price', models.DecimalField(decimal_places=2, default=0, help_text='Selling price for one base unit (e.g. one piece).', max_digits=10)),
                ('reorder_level', models.PositiveIntegerField(default=0, help_text='Trigger a low-stock alert once quantity on hand (in base units) drops to this level.')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='inventory.category')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PackagingLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g. "Box of 5", "Carton (25 pcs)"', max_length=100)),
                ('quantity_in_base_units', models.PositiveIntegerField(help_text='How many base units (pieces) this level contains in total.')),
                ('barcode', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('cost_price', models.DecimalField(blank=True, decimal_places=2, help_text="Leave blank to auto-calculate as the item's base cost × quantity.", max_digits=10, null=True)),
                ('sell_price', models.DecimalField(blank=True, decimal_places=2, help_text="Leave blank to auto-calculate as the item's base sell price × quantity.", max_digits=10, null=True)),
                ('is_purchase_unit', models.BooleanField(default=False, help_text='Can this level be ordered from a supplier (Purchasing module)?')),
                ('is_sale_unit', models.BooleanField(default=True, help_text='Can this level be sold at the till?')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packaging_levels', to='inventory.item')),
            ],
            options={
                'ordering': ['quantity_in_base_units'],
            },
        ),
    ]
