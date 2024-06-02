from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
class SendFriendRequestThrottle(UserRateThrottle):
    scope = 'send_friend_request'

class SendFriendRequestAPI(APIView):
    throttle_classes = [SendFriendRequestThrottle]

    def get(self, request, *args, **kwargs):
        # Your view logic here
        return Response({"message": "Friend request sent"}, status=status.HTTP_200_OK)