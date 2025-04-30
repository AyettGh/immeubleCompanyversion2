from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product, Category, Wishlist

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'role', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['email', 'role']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(User, CustomUserAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'created_by', 'created_at']
    search_fields = ['name', 'category__name']
    list_filter = ['category']

    def has_add_permission(self, request):
        return request.user.role == 'ADMIN'

    def has_change_permission(self, request, obj=None):
        return request.user.role == 'ADMIN'

    def has_delete_permission(self, request, obj=None):
        return request.user.role == 'ADMIN'

admin.site.register(Product, ProductAdmin)

admin.site.register(Category)
admin.site.register(Wishlist)
