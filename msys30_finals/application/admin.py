from django.contrib import admin
from .models import Product, Supplier, ReorderAlert

admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(ReorderAlert)

