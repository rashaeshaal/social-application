from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email 
    


class FriendRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def accept(self):
        self.status = self.STATUS_ACCEPTED
        self.save()

    def reject(self):
        self.status = self.STATUS_REJECTED
        self.save()

    
class Friendship(models.Model):
    STATUS_ACCEPTED = 'accepted'
    STATUS_PENDING = 'pending'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_REJECTED, 'Rejected'),
    ]
    user1 = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user1', 'user2']

    def __str__(self):
        return f"{self.user1.email} - {self.user2.username}"
 
