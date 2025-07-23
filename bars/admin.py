from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Bar, BarPhoto, UserProfile, BarComment


@admin.register(Bar)
class BarAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'price_range', 'cana_price', 'crowd_level', 'last_visited']
    list_filter = ['price_range', 'crowd_level', 'last_visited']
    search_fields = ['name', 'address', 'specialties', 'tags']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(BarPhoto)
class BarPhotoAdmin(admin.ModelAdmin):
    list_display = ['bar', 'caption', 'uploaded_by', 'is_featured', 'uploaded_at', 'image_preview']
    list_filter = ['is_featured', 'uploaded_at', 'bar', 'uploaded_by']
    search_fields = ['bar__name', 'caption', 'uploaded_by__username']
    list_editable = ['is_featured']
    actions = ['make_featured', 'remove_featured', 'delete_selected_photos']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-width: 100px; max-height: 100px; object-fit: cover;" />'
        return "No image"
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"
    
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
    remove_featured.short_description = "Remove featured status"
    
    def delete_selected_photos(self, request, queryset):
        count = queryset.count()
        for photo in queryset:
            photo.delete()  # This will trigger our custom delete method
        self.message_user(request, f'{count} photo(s) and their files deleted successfully.')
    delete_selected_photos.short_description = "Delete selected photos and files"


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


@admin.register(BarComment)
class BarCommentAdmin(admin.ModelAdmin):
    list_display = ['bar', 'user', 'comment_preview', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at', 'bar']
    search_fields = ['bar__name', 'user__username', 'comment']
    list_editable = ['is_approved']
    date_hierarchy = 'created_at'
    actions = ['approve_comments', 'unapprove_comments']
    
    def comment_preview(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = "Comment Preview"
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comment(s) approved.')
    approve_comments.short_description = "Approve selected comments"
    
    def unapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comment(s) unapproved.')
    unapprove_comments.short_description = "Unapprove selected comments"


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
