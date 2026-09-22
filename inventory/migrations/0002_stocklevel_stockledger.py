import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outlets', '0001_initial'),
        ('inventory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StockLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0, help_text='Current quantity on hand, in base units.')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_levels', to='inventory.item')),
                ('outlet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_levels', to='outlets.outlet')),
            ],
            options={
                'ordering': ['item__name'],
            },
        ),
        migrations.CreateModel(
            name='StockLedger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_qty', models.IntegerField(help_text='Positive for stock in, negative for stock out. Never zero.')),
                ('balance_after', models.IntegerField(help_text='Quantity on hand immediately after this entry, in base units.')),
                ('reason', models.CharField(choices=[('purchase_receipt', 'Purchase receipt (goods received)'), ('sale', 'Sale'), ('sale_void', 'Sale voided / refunded'), ('damage', 'Damaged / written off'), ('adjustment', 'Manual adjustment'), ('transfer_in', 'Transfer in from another outlet'), ('transfer_out', 'Transfer out to another outlet')], max_length=20)),
                ('reference', models.CharField(blank=True, help_text='Optional free-text reference, e.g. a receipt or PO number.', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stock_ledger_entries', to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ledger_entries', to='inventory.item')),
                ('outlet', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ledger_entries', to='outlets.outlet')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='stocklevel',
            constraint=models.UniqueConstraint(fields=('item', 'outlet'), name='unique_stocklevel_item_outlet'),
        ),
    ]
