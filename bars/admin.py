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
    list_display = ['bar', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['bar__name', 'caption']


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
