from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from import_export.admin import ImportExportModelAdmin
from .models import Post, BlogCategory, Comment
from .resources import PostResource, BlogCategoryResource, CommentResource


class CommentInline(TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['user', 'guest_name', 'content', 'created_at']
    can_delete = True


@admin.register(BlogCategory)
class BlogCategoryAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = BlogCategoryResource
    list_display = ['name', 'slug', 'post_count', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ['name']}
    
    @display(description='Posts')
    def post_count(self, obj):
        return obj.posts.count()


@admin.register(Post)
class PostAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = PostResource
    list_display = ['title', 'category', 'author', 'status', 'is_featured', 'view_count', 'published_at']
    list_filter = ['status', 'is_featured', 'category', 'author']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ['title']}
    date_hierarchy = 'published_at'
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image')
        }),
        ('Organization', {
            'fields': ('category', 'tags', 'author')
        }),
        ('Publishing', {
            'fields': ('status', 'published_at', 'is_featured')
        }),
        ('Social Sharing', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('tab',),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('tab',),
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('tab',),
        }),
    )
    
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = CommentResource
    list_display = ['post', 'user_display', 'content_preview', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['post__title', 'user__email', 'guest_name', 'content']
    list_editable = ['is_approved']
    
    @display(description='Author')
    def user_display(self, obj):
        return obj.user.email if obj.user else obj.guest_name
    
    @display(description='Comment')
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
