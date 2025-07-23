from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Bar, BarPhoto, UserProfile


@admin.register(Bar)
class BarAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'price_range', 'cana_price', 'crowd_level', 'last_visited']
    list_filter = ['price_range', 'crowd_level', 'last_visited']
    search_fields = ['name', 'address', 'specialties', 'tags']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(BarPhoto)
class BarPhotoAdmin(admin.ModelAdmin):
    list_display = ['bar', 'caption', 'is_featured', 'uploaded_at']
    list_filter = ['is_featured', 'uploaded_at']
    search_fields = ['bar__name', 'caption']
    list_editable = ['is_featured']
    actions = ['make_featured', 'remove_featured']
    
    def make_featured(self, request, queryset):
        updated = 0
        for photo in queryset:
            # Unfeatured other photos of the same bar first
            BarPhoto.objects.filter(bar=photo.bar, is_featured=True).update(is_featured=False)
            # Then feature this photo
            photo.is_featured = True
            photo.save()
            updated += 1
        self.message_user(request, f'{updated} photo(s) marked as featured.')
    make_featured.short_description = "Mark selected photos as featured"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} photo(s) removed from featured.')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'can_write', 'created_at']
    list_filter = ['can_write', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']


# Custom UserAdmin with UserProfile inline
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['can_write']


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
