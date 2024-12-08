from django.db import models

# Create your models here.
class Users(models.Model):
    id = models.CharField(max_length=100, primary_key=True)  # String for IDs from CSV
    name = models.CharField(max_length=100)  # String for user names
    emails = models.EmailField() 


class Products(models.Model):
    id = models.CharField(max_length=100, primary_key=True)  # String for IDs from CSV
    name = models.CharField(max_length=100)  # Product name
    price = models.FloatField()

class Orders(models.Model):
    id = models.CharField(max_length=100, primary_key=True)  # String for IDs from CSV
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)  # Foreign key to Users
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)  # Foreign key to Products
    quantity = models.IntegerField() 
