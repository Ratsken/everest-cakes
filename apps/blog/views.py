from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Q

from .models import Post, BlogCategory, Comment


class BlogListView(ListView):
    """Blog listing page"""
    model = Post
    template_name = 'blog/list.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Post.objects.filter(status='published').select_related('author', 'category')
        
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(excerpt__icontains=search)
            )
        
        if self.request.GET.get('featured'):
            queryset = queryset.filter(is_featured=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.filter(is_active=True)
        context['featured_posts'] = Post.objects.filter(status='published', is_featured=True)[:3]
        context['current_category'] = self.request.GET.get('category')
        return context


class BlogDetailView(DetailView):
    """Blog detail view with social sharing"""
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('author', 'category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        
        # Increment view count
        post.increment_view_count()
        
        # Related posts
        context['related_posts'] = Post.objects.filter(
            status='published',
            category=post.category
        ).exclude(id=post.id)[:3]
        
        # Comments
        context['comments'] = post.comments.filter(is_approved=True, parent__isnull=True)
        
        # Social sharing metadata
        context['og_title'] = post.og_title or post.title
        context['og_description'] = post.og_description or post.excerpt
        context['og_image'] = post.og_image.url if post.og_image else (post.featured_image.url if post.featured_image else None)
        
        return context


class BlogCategoryView(ListView):
    """Blog category page"""
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        self.category = get_object_or_404(BlogCategory, slug=self.kwargs['slug'], is_active=True)
        return Post.objects.filter(status='published', category=self.category)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = BlogCategory.objects.filter(is_active=True)
        return context


@require_POST
def submit_comment(request, slug):
    """Submit a blog comment"""
    post = get_object_or_404(Post, slug=slug, status='published')
    
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id')
    
    if not content:
        return JsonResponse({'error': 'Comment cannot be empty'}, status=400)
    
    parent = None
    if parent_id:
        try:
            parent = Comment.objects.get(id=parent_id, post=post)
        except Comment.DoesNotExist:
            pass
    
    if request.user.is_authenticated:
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            content=content,
            parent=parent
        )
    else:
        guest_name = request.POST.get('name', '').strip()
        guest_email = request.POST.get('email', '').strip()
        
        if not all([guest_name, guest_email]):
            return JsonResponse({'error': 'Name and email are required'}, status=400)
        
        comment = Comment.objects.create(
            post=post,
            guest_name=guest_name,
            guest_email=guest_email,
            content=content,
            parent=parent
        )
    
    if request.htmx:
        comments = post.comments.filter(is_approved=True, parent__isnull=True)
        return render(request, 'blog/partials/comments.html', {'comments': comments, 'post': post})
    
    return JsonResponse({'success': True, 'comment_id': comment.id})
