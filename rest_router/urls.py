from django.conf.urls import patterns, include, url
from rest_router import views

urlpatterns = [
    url(r'^(?P<service>\w+)/(?P<url>.*)$', views.proxy, name="proxy"),
]
