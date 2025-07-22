import uuid
from django.db import models
from django.urls import reverse


class Bar(models.Model):
    PRICE_RANGE_CHOICES = [
        ('€', '€'),
        ('€€', '€€'),
        ('€€€', '€€€'),
    ]
    
    CROWD_LEVEL_CHOICES = [
        ('quiet', 'Quiet'),
        ('medium', 'Medium'),
        ('crowded', 'Crowded'),
    ]
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    address = models.TextField()
    notes = models.TextField()
    
    # Location fields
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    map_link = models.URLField(blank=True)
    
    # Bar details
    specialties = models.TextField(blank=True)
    price_range = models.CharField(max_length=3, choices=PRICE_RANGE_CHOICES, blank=True)
    cana_price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, 
                                   help_text="Price in euros")
    crowd_level = models.CharField(max_length=10, choices=CROWD_LEVEL_CHOICES, blank=True)
    last_visited = models.DateField(null=True, blank=True)
    tags = models.TextField(blank=True, help_text="Comma-separated tags")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_visited', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('bars:detail', kwargs={'pk': self.pk})
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []


class BarPhoto(models.Model):
    bar = models.ForeignKey(Bar, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='bars/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Photo for {self.bar.name}"
