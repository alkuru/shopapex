from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .supplier_models import Supplier

class SearchCache(models.Model):
    cache_key = models.CharField(max_length=255, unique=True)
    query_type = models.CharField(max_length=50)
    query_params = models.JSONField()
    result_data = models.JSONField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    hit_count = models.PositiveIntegerField(default=1)
    class Meta:
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['query_type', 'supplier']),
        ]

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=50, null=True, blank=True)
    query = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True)
    found_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']

class SavedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    article = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    item_key = models.CharField(max_length=100)
    supplier_code = models.CharField(max_length=100)
    original_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['user', 'supplier', 'item_key']

class OrderedProduct(models.Model):
    article = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order_data = models.JSONField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['article', 'brand']),
            models.Index(fields=['created_at']),
        ]
