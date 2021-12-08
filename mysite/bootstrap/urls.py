from django.contrib import admin
from django.urls import path, include
from bootstrap import settings
from django.conf.urls.static import static
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('<filename>.html', views.html),

    path('generate_reports/', views.generate_reports),
    path('visualize_tweet_report/', views.visualize_tweet_report, name='visualize_tweet_report'),
    path('fetch_word_cloud/', views.fetch_word_cloud, name='fetch_word_cloud'),
    path('fetch_tweet/', views.fetch_tweet),

    path('accounts/', include('allauth.urls')),
    path('', views.index),


    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
