from rest_framework import permissions
from .models import Product, Group


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        path = request.get_full_path()
        split_path = path.split("/")
        if len(split_path) == 4:
            return True
        product_id = int(split_path[3])
        product = Product.objects.get(id=product_id)
        author = product.author
        return author == user


class IsAuthorOrIsStudent(permissions.BasePermission):
    message = "You haven't buy this product yet."

    def has_permission(self, request, view):
        if not request.user:
            return False

        user = request.user
        path = request.get_full_path()
        split_path = path.split("/")
        if len(split_path) == 4:
            return True
        product_id = int(split_path[3])
        product = Product.objects.get(id=product_id)
        author = product.author
        if author == user:
            return True

        if not request.method in permissions.SAFE_METHODS:
            return False

        product_groups = Group.objects.filter(product=product)
        students = []
        for group in product_groups:
            for student in group.users.all():
                students.append(student)
        if user in students:
            return True
