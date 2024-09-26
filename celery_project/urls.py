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
    path('many/', views.send_many, name="send_many"),
    path('on_delivery/', views.render_on_delivery, name='on_delivery'),
    path('stress/', views.stress, name="stress"),
    path('stress_many/', views.stress_many, name="stress_many"),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('products/', views.product_list, name="product_list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
