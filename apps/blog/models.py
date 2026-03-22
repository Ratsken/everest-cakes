from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager
import uuid


class BlogCategory(models.Model):
    """Blog Category"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Blog Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category', args=[self.slug])


class Post(models.Model):
    """Blog Post"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.CharField(max_length=300, blank=True)
    content = RichTextField()
    
    # Category & Tags
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    tags = TaggableManager(blank=True)
    
    # Featured Image
    featured_image = models.ImageField(upload_to='blog/')
    
    # Author
    author = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='posts')
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    og_image = models.ImageField(upload_to='blog/social/', blank=True)
    
    # Social Sharing
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.TextField(blank=True)
    
    # Engagement
    view_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:detail', args=[self.slug])
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


class Comment(models.Model):
    """Blog Comments"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Author (if authenticated)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, null=True, blank=True)
    
    # Guest info
    guest_name = models.CharField(max_length=200, blank=True)
    guest_email = models.EmailField(blank=True)
    
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        author = self.user.email if self.user else self.guest_name
        return f"Comment by {author} on {self.post.title}"
