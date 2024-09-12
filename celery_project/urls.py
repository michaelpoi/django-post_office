from django.contrib import admin
from django.urls import path, include
from celery_project import views

urlpatterns = [
    path('', views.home, name='home'),
    path("admin/", admin.site.urls),
    path("index/", views.index, name="index"),
    path('send_template/', views.send_template, name="send_template"),
    path('send_image/', views.send_image, name="send_image"),
    path('send_attachment/', views.send_attachment, name="send_attachment"),
    path('templating/', views.test_new_system, name="test_new_system"),
    path('many/', views.send_many, name="send_many"),
    path('inline/', views.test_render_image, name='inlines')
]
