from django.shortcuts import render
from django.db.models import Q

# Create your views here.

from django.contrib.auth import get_user_model, login, logout  # new
from django.contrib.auth.forms import AuthenticationForm  # new
from rest_framework import generics, permissions, status, views, viewsets  # new
from rest_framework.response import Response

from .models import Trip
from .serializers import TripSerializer, UserSerializer


class SignUpView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


# new
class LogInView(views.APIView):
    def post(self, request):
        form = AuthenticationForm(data=request.data)
        if form.is_valid():
            user = form.get_user()
            login(request, user=form.get_user())
            return Response(UserSerializer(user).data)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


# new
class LogOutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, *args, **kwargs):
        logout(self.request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TripView(viewsets.ReadOnlyModelViewSet):
    lookup_field = "id"  # new
    lookup_url_kwarg = "trip_id"  # new
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TripSerializer

    # new
    def get_queryset(self):
        user = self.request.user
        if user.group == "driver":
            return Trip.objects.filter(Q(status=Trip.REQUESTED) | Q(driver=user))
        if user.group == "rider":
            return Trip.objects.filter(rider=user)
        return Trip.objects.none()
