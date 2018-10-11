from django.contrib import admin
from .models import Category, Blog

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name')
    ordering = ('id', )

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'read_num', 'blog_category', 'author', 'created_time', 'last_updated_time')
    ordering = ('id', )
