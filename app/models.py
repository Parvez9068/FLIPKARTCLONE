from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class CustomManager(models.Manager):
    def Cloths_list(self):
        return self.filter(category__exact="Cloths")
    def Shoes_list(self):
        return self.filter(category__exact="Shoes")
    def Mobile_list(self):
        return self.filter(category__exact="Mobile")
    
    def Electronics_list(self):
        return self.filter(category__exact="Electronics")
    
    def Fashion_list(self):
        return self.filter(category__exact="Fashion")
    
    def Grocery_list(self):
        return self.filter(category__exact="Grocery")
    
class Product(models.Model):
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    productid = models.IntegerField(primary_key=True)
    productname = models.CharField(max_length=100)
    type = (
        ("Cloths", "Cloths"),
        ("Shoes", "Shoes"),
        ("Mobile", "Mobile"),
        ("Electronics", "Electronics"),
        ("Fashion", "Fashion"),
        ("Grocery", "Grocery"),
    )
    category = models.CharField(max_length=50, choices=type)
    description = models.TextField()
    price = models.FloatField()
    images = models.ImageField(upload_to="photos")
    object=models.Manager()
    productmanager=CustomManager()


class Cart(models.Model):
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    productid = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    qty = models.PositiveIntegerField(default=0)


class Orders(models.Model):
    orderid = models.IntegerField(primary_key=True)
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    productid = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    qty = models.PositiveIntegerField(default=0)


class Address(models.Model):
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    contactnum = models.IntegerField()
    addr = models.TextField()
    pincode = models.IntegerField()


class Payment(models.Model):
    receiptid = models.IntegerField(primary_key=True)
    orderid = models.ForeignKey(Orders, on_delete=models.SET_NULL, null=True)
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    productid = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    totalprice = models.FloatField()

    
