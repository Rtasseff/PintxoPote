from django.contrib import admin
from .models import Bar, BarPhoto


@admin.register(Bar)
class BarAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'price_range', 'cana_price', 'crowd_level', 'last_visited']
    list_filter = ['price_range', 'crowd_level', 'last_visited']
    search_fields = ['name', 'address', 'specialties', 'tags']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(BarPhoto)
class BarPhotoAdmin(admin.ModelAdmin):
    list_display = ['bar', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['bar__name', 'caption']
