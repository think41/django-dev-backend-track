"""
Serializers for the Books app.

This module contains all serializers for book-related API endpoints,
including search, CRUD operations, and inventory management.
"""

from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    """
    General purpose book serializer for most endpoints.
    Includes computed fields for availability status.
    """
    
    is_available = serializers.ReadOnlyField()
    borrowed_copies = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = (
            'id', 'title', 'author', 'genre', 'total_copies',
            'available_copies', 'created_at', 'is_available', 
            'borrowed_copies'
        )
        read_only_fields = ('id', 'created_at')


class BookSearchSerializer(serializers.ModelSerializer):
    """
    Serializer for book search results.
    Optimized for public search endpoints with essential information.
    """
    
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = (
            'id', 'title', 'author', 'genre', 
            'available_copies', 'is_available'
        )


class BookCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new books.
    Validates input and sets available_copies equal to total_copies by default.
    """
    
    class Meta:
        model = Book
        fields = ('title', 'author', 'genre', 'total_copies')
    
    def validate_title(self, value):
        """Ensure title is not empty after stripping whitespace."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()
    
    def validate_author(self, value):
        """Ensure author is not empty after stripping whitespace."""
        if not value.strip():
            raise serializers.ValidationError("Author cannot be empty.")
        return value.strip()
    
    def validate_total_copies(self, value):
        """Ensure total_copies is at least 1."""
        if value < 1:
            raise serializers.ValidationError("Total copies must be at least 1.")
        return value
    
    def create(self, validated_data):
        """Create book with available_copies set to total_copies."""
        validated_data['available_copies'] = validated_data['total_copies']
        return super().create(validated_data)


class BookUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing books.
    Handles inventory adjustments when total_copies changes.
    """
    
    class Meta:
        model = Book
        fields = ('title', 'author', 'genre', 'total_copies')
    
    def validate_title(self, value):
        """Ensure title is not empty after stripping whitespace."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()
    
    def validate_author(self, value):
        """Ensure author is not empty after stripping whitespace."""
        if not value.strip():
            raise serializers.ValidationError("Author cannot be empty.")
        return value.strip()
    
    def validate_total_copies(self, value):
        """Ensure total_copies is at least the number of borrowed copies."""
        if hasattr(self, 'instance') and self.instance:
            borrowed = self.instance.borrowed_copies
            if value < borrowed:
                raise serializers.ValidationError(
                    f"Total copies cannot be less than currently borrowed copies ({borrowed})."
                )
        if value < 1:
            raise serializers.ValidationError("Total copies must be at least 1.")
        return value
    
    def update(self, instance, validated_data):
        """Update book and adjust available copies if total_copies changed."""
        new_total_copies = validated_data.get('total_copies')
        
        if new_total_copies and new_total_copies != instance.total_copies:
            # Update all fields first
            for field, value in validated_data.items():
                if field != 'total_copies':
                    setattr(instance, field, value)
            
            # Use the model method to properly handle copies adjustment
            instance.update_copies(new_total_copies)
        else:
            # Regular update for other fields
            for field, value in validated_data.items():
                setattr(instance, field, value)
            instance.save()
        
        return instance


class AdminBookListSerializer(serializers.ModelSerializer):
    """
    Serializer for admin book list view with additional management information.
    """
    
    is_available = serializers.ReadOnlyField()
    borrowed_copies = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = (
            'id', 'title', 'author', 'genre', 'total_copies',
            'available_copies', 'borrowed_copies', 'is_available', 'created_at'
        )