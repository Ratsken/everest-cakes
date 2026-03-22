from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='list'),
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='detail'),
    path('<slug:slug>/comment/', views.submit_comment, name='submit_comment'),
    path('category/<slug:slug>/', views.BlogCategoryView.as_view(), name='category'),
]
