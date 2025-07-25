import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extends Django User model with PintxoPote-specific permissions
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    can_write = models.BooleanField(
        default=False, 
        help_text="Allow this user to add, edit, and manage bars"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({'Writer' if self.can_write else 'Reader'})"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


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
    
    def get_display_photo(self):
        """Return the featured photo, or the most recent photo if no featured photo"""
        featured_photo = self.photos.filter(is_featured=True).first()
        if featured_photo:
            return featured_photo
        return self.photos.first()
    
    def get_google_maps_url(self):
        """Return Google Maps URL for this bar's location"""
        import urllib.parse
        
        # If we have coordinates, use them for more accuracy
        if self.latitude and self.longitude:
            # Use coordinates for precise location
            query = f"{self.latitude},{self.longitude}"
        else:
            # Fall back to address search
            query = f"{self.name}, {self.address}"
        
        # URL encode the query
        encoded_query = urllib.parse.quote(query)
        
        # Return Google Maps URL that works on mobile and desktop
        return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"


class BarPhoto(models.Model):
    bar = models.ForeignKey(Bar, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='bars/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        help_text="User who uploaded this photo"
    )
    is_featured = models.BooleanField(
        default=False, 
        help_text="Display this photo on the home page list for this bar"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', '-uploaded_at']
    
    def __str__(self):
        featured_text = " (Featured)" if self.is_featured else ""
        uploader_text = f" by {self.uploaded_by.username}" if self.uploaded_by else ""
        return f"Photo for {self.bar.name}{featured_text}{uploader_text}"
    
    def save(self, *args, **kwargs):
        # Ensure only one featured photo per bar
        if self.is_featured:
            BarPhoto.objects.filter(bar=self.bar, is_featured=True).update(is_featured=False)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Delete the actual image file when the model instance is deleted
        if self.image:
            if self.image.storage.exists(self.image.name):
                self.image.storage.delete(self.image.name)
        super().delete(*args, **kwargs)


class BarComment(models.Model):
    """
    User comments on bars - allows any logged-in user to share experiences
    """
    bar = models.ForeignKey(Bar, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(
        max_length=1000,
        help_text="Share your experience at this bar (max 1000 characters)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(
        default=True,
        help_text="Admin can moderate inappropriate comments"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bar Comment"
        verbose_name_plural = "Bar Comments"
    
    def __str__(self):
        return f"{self.user.username} on {self.bar.name}: {self.comment[:50]}..."
