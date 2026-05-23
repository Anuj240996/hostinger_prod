from django.contrib import admin
from .models import Permission, Role, RolePermission, UserRole, Feature, OrganizationFeature, SubscriptionPlan, PlanFeature, OrganizationSubscription

class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization']
    list_filter = ['organization']
    inlines = [RolePermissionInline]
    search_fields = ['name']

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['codename', 'name', 'app_label', 'model']
    search_fields = ['codename', 'name']

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission']

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'organization']
    list_filter = ['organization']

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['codename', 'enabled_by_default']

@admin.register(OrganizationFeature)
class OrganizationFeatureAdmin(admin.ModelAdmin):
    list_display = ['organization', 'feature', 'enabled']

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'monthly_price', 'max_users', 'is_active']

@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display = ['plan', 'feature', 'enabled']

@admin.register(OrganizationSubscription)
class OrganizationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['organization', 'plan', 'status', 'start_date']