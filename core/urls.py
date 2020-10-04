from django.urls import path

from . import views

urlpatterns = [
    path('', views.test, name='test'),
    path('report', views.report, name='report'),
    path('history', views.history, name='history')
]
