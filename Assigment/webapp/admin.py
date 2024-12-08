from django.contrib import admin
from .models import Users,Orders,Products

class UsersAdmin(admin.ModelAdmin):
    list_display = ["id","name","emails"]

class ProductsAdmin(admin.ModelAdmin):
    list_display = ["id","name","price"]

class OrdersAdmin(admin.ModelAdmin):
    list_display = ["id","user_id","product_id","quantity"]

admin.site.register(Users,UsersAdmin)
admin.site.register(Orders,OrdersAdmin)
admin.site.register(Products,ProductsAdmin)
# Register your models here.
