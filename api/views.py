from django.shortcuts import render
from rest_framework import viewsets, permissions, generics
from .models import Entry
from .serializers import EntrySerializer, RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

# Create your views here.

class EntryViewSet(viewsets.ModelViewSet):
    serializer_class = EntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        obj = get_object_or_404(Entry, pk=self.kwargs["pk"])
        if obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this entry.")
        return obj

class RegisterView(generics.CreateAPIView):
    queryset = Entry.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer
