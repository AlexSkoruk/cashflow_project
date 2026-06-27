from django.contrib import admin
from .models import Status, Type, Category, Subcategory, CashFlowRecord

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'operation_type')
    list_filter = ('operation_type',)
    search_fields = ('name',)
    list_editable = ('operation_type',)

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    list_filter = ('category__operation_type', 'category')
    search_fields = ('name',)

@admin.register(CashFlowRecord)
class CashFlowRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'status', 'operation_type', 'category', 'subcategory', 'amount')
    list_filter = ('status', 'operation_type', 'category', 'subcategory', 'date')
    search_fields = ('comment', 'amount')
    date_hierarchy = 'date'