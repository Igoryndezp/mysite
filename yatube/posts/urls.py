from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('posts/<int:post_id>/comment/',
         views.comment_post, name='comment_post'),
    path('edit/', views.edit_profile, name='edit'),
    path('<int:pk>/like/', views.add_like, name='like'),
    path('<int:pk>/dislike/', views.add_dislike, name='dislike'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    path('directs/', views.inbox, name='inbox'),
    path('directs/<username>', views.directs, name='directs'),
    path('new/', views.user_search, name='usersearch'),
    path('new/<username>', views.new_conversation, name='newconversation'),
    path('send/', views.send_direct, name='send_direct'),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
