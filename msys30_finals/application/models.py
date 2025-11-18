from django.db import models

# ----------------------------
# SUPPLIER MODEL
# ----------------------------
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


# ----------------------------
# PRODUCT MODEL
# ----------------------------
class Product(models.Model):
    sku = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def is_low_stock(self):
        """Check if current stock is below or equal to reorder level."""
        return self.quantity <= self.reorder_level


# ----------------------------
# REORDER ALERT MODEL
# ----------------------------
class ReorderAlert(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    safety_stock = models.PositiveIntegerField(default=0)
    reorder_point = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reorder Alert: {self.product.name}"
