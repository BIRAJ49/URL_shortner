from django.urls import path

from . import views

app_name = 'shortener'

urlpatterns = [
    path('', views.ShortURLListView.as_view(), name='list'),
    path('create/', views.ShortURLCreateView.as_view(), name='create'),
    path('urls/<int:pk>/', views.ShortURLDetailView.as_view(), name='detail'),
    path('urls/<int:pk>/edit/', views.ShortURLUpdateView.as_view(), name='edit'),
    path('urls/<int:pk>/delete/', views.ShortURLDeleteView.as_view(), name='delete'),
    path('urls/<int:pk>/qr/', views.qr_code, name='qr'),
    path('<slug:key>/', views.redirect_short_url, name='redirect'),
]
