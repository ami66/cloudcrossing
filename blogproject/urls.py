from django.conf.urls import url, include
from django.contrib import admin
from blog.feeds import AllPostsRssFeed

from users import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('blog.urls')),
    url(r'', include('comments.urls')),
    url(r'^all/rss/$', AllPostsRssFeed(), name='rss'),
    url(r'^search/', include('haystack.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^users/', include('django.contrib.auth.urls')),
    url(r'^$', views.index, name='index'),
    url(r'mdeditor/', include('mdeditor.urls')),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
