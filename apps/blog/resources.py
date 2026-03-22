from import_export import resources
from .models import Post, BlogCategory, Comment


class BlogCategoryResource(resources.ModelResource):
    class Meta:
        model = BlogCategory
        fields = ('id', 'name', 'slug', 'description', 'order', 'is_active')
        export_order = fields


class PostResource(resources.ModelResource):
    class Meta:
        model = Post
        fields = (
            'id', 'title', 'slug', 'excerpt', 'category__name', 'author__email',
            'status', 'published_at', 'is_featured', 'meta_title',
            'meta_description', 'og_title', 'og_description', 'view_count',
            'created_at', 'updated_at'
        )
        export_order = fields


class CommentResource(resources.ModelResource):
    class Meta:
        model = Comment
        fields = (
            'id', 'post__title', 'parent__id', 'user__email', 'guest_name',
            'guest_email', 'content', 'is_approved', 'created_at'
        )
        export_order = fields
