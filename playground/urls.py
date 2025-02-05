from django.urls import path
from . import views
from . import views2
from . import views3

urlpatterns = [
    # path('hello/', views.say_hello),
    path('hardAI/', views.get_best_move, name = 'hardAI'),
    path('easyAI/', views2.get_best_move, name = 'easyAI'),
    path('mediumAI/', views3.get_best_move, name = 'mediumAI')
]
