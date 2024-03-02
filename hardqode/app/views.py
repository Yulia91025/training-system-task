from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Product, Lesson, Group
from .serializers import (
    ProductSerializer,
    LessonSerializer,
    GroupSerializer,
    UserSerializer,
)
from .permissions import IsAuthorOrReadOnly, IsAuthorOrIsStudent
from .utils import GroupDistributionUtil


class ProductsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        products = Product.objects.all()
        return products

    @action(methods=["get"], detail=True)
    def buy(self, request, pk=None):
        user = self.request.user
        product = Product.objects.get(id=pk)
        group_distr = GroupDistributionUtil(product)
        group = group_distr.manage(user)
        if not group:
            return Response({"error": "You already buy this product!"})
        return Response({"group": GroupSerializer(group).data})


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthorOrIsStudent]

    def get_queryset(self):
        path = self.request.get_full_path()
        product_id = int(path.split("/")[3])
        product = Product.objects.get(id=product_id)
        lessons = Lesson.objects.filter(product=product)
        return lessons


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthorOrIsStudent]

    def get_queryset(self):
        path = self.request.get_full_path()
        product_id = int(path.split("/")[3])
        product = Product.objects.get(id=product_id)
        groups = Group.objects.filter(product=product)
        return groups


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return [user]
