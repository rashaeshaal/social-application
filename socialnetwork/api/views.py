from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.paginator import Paginator
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from .models import User, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer
import jwt
import json

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'user_id': user.id, 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        # Print the authenticated user's details
        print(f"Authenticated User: {user.name} (ID: {user.id})")

        refresh = RefreshToken.for_user(user)

        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        })

class UserView(APIView):
    def get(self, request):
        token = request.headers.get('Authorization')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)

class UserSearchAPIView(APIView):
    def get(self, request):
        keyword = request.query_params.get('q')
        
        if not keyword:
            return Response({'message': 'No search keyword provided'}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(email__iexact=keyword) | User.objects.filter(name__icontains=keyword)
        
        paginator = Paginator(users, 10)
        page_number = request.query_params.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        serializer = UserSerializer(page_obj, many=True)
        
        return Response(serializer.data)

class SendFriendRequestAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get('receiver_id')

        if not receiver_id:
            return Response({'error': 'Receiver ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user == receiver:
            return Response({'error': 'You cannot send a friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            friend_request = FriendRequest.objects.create(from_user=request.user, to_user=receiver, status='pending')
            serializer = FriendRequestSerializer(friend_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.shortcuts import get_object_or_404

from rest_framework import permissions

class HandleFriendRequestAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, request_id):
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
        except FriendRequest.DoesNotExist:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the authenticated user is involved in the friend request
        if request.user != friend_request.to_user:
            return Response({'error': 'Permission denied: User not authorized to handle this request'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the friend request is pending
        if friend_request.status != FriendRequest.STATUS_PENDING:
            return Response({'error': 'Friend request is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Accept or reject the friend request based on the action parameter
        action = request.data.get('action')
        if action == 'accept':
            friend_request.accept()
            return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)
        elif action == 'reject':
            friend_request.reject()
            return Response({'message': 'Friend request rejected'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)


class PendingFriendRequestsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            print("User:", request.user)

            pending_requests = FriendRequest.objects.filter(to_user=request.user, status='pending')
            print("Pending Requests:", pending_requests)

            serializer = FriendRequestSerializer(pending_requests, many=True)
            print("Serialized Data:", serializer.data)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error occurred:", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
from django.http import JsonResponse

def list_accepted_friends(request):
    accepted_requests = FriendRequest.objects.filter(status=FriendRequest.STATUS_ACCEPTED)
    accepted_users = set()
    for request in accepted_requests:
        accepted_users.add(request.from_user)
        accepted_users.add(request.to_user)
    
    accepted_users_data = [{"id": user.id, "name": user.name, "email": user.email} for user in accepted_users]
    return JsonResponse(accepted_users_data, safe=False)