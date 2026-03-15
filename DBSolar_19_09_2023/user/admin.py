from django.contrib import admin
from .models import (
    Profile, Module, ModulePermission, UserModulePermission, ControlPanelAccess
)

# Register your models here.
admin.site.register(Profile)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'display_name']
    ordering = ['order', 'display_name']


@admin.register(ModulePermission)
class ModulePermissionAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'module', 'operation', 'order', 'is_active']
    list_filter = ['module', 'is_active', 'operation']
    search_fields = ['display_name', 'module__display_name']
    ordering = ['module', 'order']


@admin.register(UserModulePermission)
class UserModulePermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'module_permission', 'granted', 'granted_by', 'granted_at']
    list_filter = ['granted', 'module_permission__module', 'granted_at']
    search_fields = ['user__username', 'module_permission__module__display_name']
    readonly_fields = ['granted_at', 'updated_at']
    ordering = ['user', 'module_permission']


@admin.register(ControlPanelAccess)
class ControlPanelAccessAdmin(admin.ModelAdmin):
    list_display = ['is_active', 'last_accessed', 'last_accessed_by', 'updated_at']
    readonly_fields = ['last_accessed', 'last_accessed_by', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not ControlPanelAccess.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
