from django.urls import path
from .views import (
    index,
    signup,
    signin,
    logout_user,
    setting,
    upload,
    profile,
    like,
    delete_post,
    follow,
    search
)

urlpatterns = [
    path('', index, name='index'),
    path('signup/', signup, name= 'signup'),
    path('signin/', signin, name= 'signin'),
    path('logout/', logout_user, name= 'logout'),
    path('settings/', setting, name='setting'),
    path('profile/<str:username>', profile, name='profile'),
    path('upload/', upload, name='upload'),
    path('delete/', delete_post, name='delete_post'),
    path('like/', like, name='like'),
    path('follow/', follow, name='follow'),
    path('search/', search, name='search'),
]

