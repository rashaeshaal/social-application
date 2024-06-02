# api/urls.py

from django.urls import path
from .views import (
    RegisterView,
    UserDetailsView,
    LoginView,
    UserView,
    UserSearchAPIView,
    SendFriendRequestAPI,
    # ListFriendsAPI,
    PendingFriendRequestsAPI,
    HandleFriendRequestAPI,
    list_accepted_friends,
     
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', UserDetailsView.as_view(), name='user-details'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/<int:pk>/', UserView.as_view(), name='user-view'),
    path('search/', UserSearchAPIView.as_view(), name='user-search'),
    path('send_friend_request/', SendFriendRequestAPI.as_view(), name='send_friend_request'),
    path('pending_friend_requests/', PendingFriendRequestsAPI.as_view(), name='pending_friend_requests'),
    path('handle-friend-request/<int:request_id>/', HandleFriendRequestAPI.as_view(), name='handle-friend-request'),
    path('api/list-accepted-friends/', list_accepted_friends, name='list_accepted_friends'), 

]
