from django.contrib import admin
from django.urls import include, path
from posts import views


urlpatterns = [
    path('', views.index, name='index'),
    path('', include('posts.urls', namespace='posts')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('about/', include('about.urls', namespace='about')),
]
