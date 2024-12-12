"""
URL configuration for email_classification project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path

from django.urls import path
from emailapp import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('', views.home_view, name='home'),
    path('classify/', views.classify_view, name='classify'),
    path('emails/', views.classify_view, name='allmails'),
    path('finance/', views.categorized_emails_view, {'category': 'finance'}, name='finance_emails'),
    path('social/', views.categorized_emails_view, {'category': 'social'}, name='social_emails'),
    path('news/', views.categorized_emails_view, {'category': 'news'}, name='news_emails'),
    path('health/', views.categorized_emails_view, {'category': 'health'}, name='health_emails'),
    path('promotions/', views.categorized_emails_view, {'category': 'promotions'}, name='promotions_emails'),
    path('job/', views.categorized_emails_view, {'category': 'job'}, name='job_emails'),
    path('finance/', views.finance_emails, name='finance_emails'),
    path('social/', views.social_emails, name='social_emails'),
    path('news/', views.news_emails, name='news_emails'),
    path('health/', views.health_emails, name='health_emails'),
    path('promotions/', views.promotions_emails, name='promotions_emails'),
    path('job/', views.job_emails, name='job_emails'),
]
