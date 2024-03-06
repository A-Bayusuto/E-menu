from django.db import models

class Menu(models.Model):
    code = models.AutoField(primary_key=True)
    item = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    summary = models.TextField(null=True, blank=True)
    picture_address = models.CharField(max_length=255, null=True, blank=True)

class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50, null=True, blank=True)

class OrderDate(models.Model):
    date_id = models.AutoField(primary_key=True)
    order_time = models.TimeField()
    order_date = models.DateField()
    order_week = models.IntegerField()
    order_month = models.IntegerField()
    order_year = models.IntegerField()

class OrderTable(models.Model):
    table_id = models.IntegerField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    date = models.ForeignKey(OrderDate, on_delete=models.CASCADE)
    order_id = models.IntegerField()
    qty = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('table_id', 'supplier', 'menu', 'date', 'order_id')