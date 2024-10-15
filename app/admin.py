from django.contrib import admin
from .models import Product,Cart,Orders,Payment,Address
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display=[
        'userid',
        'productid',
        'productname',
        'category',
        'description',
        'price',
        'images'
    ]

class CartAdmin(admin.ModelAdmin):
    list_display=[
        'userid',
        'productid',
        'qty'
    ]

class OrdersAdmin(admin.ModelAdmin):
    list_display=[
        'orderid',
        'userid',
        'productid',
        'qty'
    ]


class PaymentAdmin(admin.ModelAdmin):
    list_display=[
        'receiptid',
        'orderid',
        'userid',
        'productid',
        'totalprice'
    ]

class AddressAdmin(admin.ModelAdmin):
    list_display=[
        'userid',
        'contactnum',
        'addr',
        'pincode'
    ]

admin.site.register(Product,ProductAdmin)
admin.site.register(Cart,CartAdmin)
admin.site.register(Orders,OrdersAdmin)
admin.site.register(Payment,PaymentAdmin)
admin.site.register(Address,AddressAdmin)