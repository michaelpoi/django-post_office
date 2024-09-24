from django.contrib import admin
from django.urls import path, include
from celery_project import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path("admin/", admin.site.urls),
    path("index/", views.index, name="index"),
    path('send_template/', views.send_template, name="send_template"),
    path('send_image/', views.send_image, name="send_image"),
    path('send_attachment/', views.send_attachment, name="send_attachment"),
    path('templating/', views.test_new_system, name="test_new_system"),
    path('many/', views.send_many, name="send_many"),
    path('inline/', views.test_render_image, name='inlines'),
    path('on_delivery/', views.render_on_delivery, name='on_delivery'),
    path('stress/', views.stress, name="stress"),
    path('stress_many/', views.stress_many, name="stress_many"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
