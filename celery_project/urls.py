from django.contrib import admin
from django.urls import path, include
from celery_project import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("index/", views.index, name="index"),
    path('send_template/', views.send_template, name="send_template"),
    path('send_image/', views.send_image, name="send_image"),
    path('send_attachment/', views.send_attachment, name="send_attachment"),
    path('templating/', views.test_new_system, name="test_new_system"),
]
