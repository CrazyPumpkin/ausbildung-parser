from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.views.static import serve

from apps.site_parser.views import VacanciesView

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^vacancies/', VacanciesView.as_view(), name='vacancies-list'),
]

urlpatterns += [
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
