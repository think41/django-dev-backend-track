from rest_framework import serializers
from app.users.models import User
from app.users.models import BookRequest

class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role', 
            'is_approved', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserApprovalSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    approve = serializers.BooleanField()


class AdminBookRequestSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = BookRequest
        fields = [
            'id', 'user', 'username', 'user_email', 'book', 'book_title', 'book_author', 
            'request_date', 'borrow_date', 'return_date', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'book', 'request_date', 'created_at', 'updated_at']


class BookRequestActionSerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=['approve', 'reject'])