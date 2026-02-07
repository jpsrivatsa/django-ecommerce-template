from django.db import models
from django.contrib.auth.models import User 
from django.conf import settings
class ChangeHistory(models.Model):
    CHANGE_TYPES = [
        ('INSERT', 'Insert'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]
    CHDIR_ID = models.CharField(max_length=100, unique=True)
    entity_type = models.CharField(max_length=255)
    entity_id = models.CharField(max_length=100) # Use CharField if your IDs are strings or UUIDs
    change_type = models.CharField(max_length=50, choices=CHANGE_TYPES)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, to_field= 'username',
        related_name='chdir_created',
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Change History"
        verbose_name_plural = "Change Histories"
        ordering = ['-created_at']  # Order by most recent changes first

    def __str__(self):
        return f"{self.entity_type} {self.entity_id} {self.change_type} on {self.timestamp}"


class ChangedItem(models.Model):
    CHDIR = models.ForeignKey(ChangeHistory, related_name='changed_items', to_field = "CHDIR_ID", on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Changed Item"
        verbose_name_plural = "Changed Items"

    def __str__(self):
        return f"Change {self.change_history.change_id}: {self.field_name} changed from {self.old_value} to {self.new_value}"
