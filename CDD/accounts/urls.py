from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('',home,name='home'),
    path('register/',register,name='register'),
    path('login/',user_login,name='login'),
    path('logout/', logout_view, name='logout'),
    path('upload/', upload, name='upload'),
    path('type/', type, name='plant_type'),
    path('board/', board, name='dashboard'),
    path('upload_image/', upload_image, name='upload_image'),
    path('croprec/', Crop_Recommendation, name='crop_rec'),
    path('fertrec/', Fertilizer_Recommendation, name='fert_rec'),
    path('pestrec/<int:Did>/', pest_rec, name='pest_rec'),
]