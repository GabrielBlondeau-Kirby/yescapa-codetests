from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('v1/search/campers/', views.v1_search_closer_campers, ),
    path('v2/search/campers/', views.v2_search_closer_campers, ),
    path('v3/search/campers/', views.v3_search_closer_campers, ),
]
