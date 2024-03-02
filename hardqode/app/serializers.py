from rest_framework import serializers
from .models import Product, Lesson, Group
from django.contrib.auth.models import User


class CurrentProductDefault:
    requires_context = True

    def __call__(self, serializer_field):
        request = serializer_field.context["request"]
        path = request.get_full_path()
        product_id = int(path.split("/")[3])
        self.product = Product.objects.get(id=product_id)
        return self.product


class ProductSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author_username = serializers.SerializerMethodField("get_author")
    lessons_count = serializers.SerializerMethodField("get_lessons_count")
    students_count = serializers.SerializerMethodField("get_students_count")
    fullness_percentage = serializers.SerializerMethodField("get_fullness_percentage")
    purchase_percentage = serializers.SerializerMethodField("get_purchase_percentage")

    class Meta:
        model = Product
        fields = "__all__"

    def get_author(self, product):
        user = product.author
        return user.username

    def get_lessons_count(self, product):
        lessons = Lesson.objects.filter(product=product)
        return len(lessons)

    def get_students_count(self, product):
        groups = Group.objects.filter(product=product)
        students = []
        for group in groups:
            for student in group.users.all():
                students.append(student)
        return len(students)

    def get_fullness_percentage(self, product):
        groups = Group.objects.filter(product=product)
        if not len(groups):
            return 0
        max_users_count = product.max_group_students
        groups_users_counts = [len(group.users.all()) for group in groups]
        avg_users_count = sum(groups_users_counts) / len(groups)
        percentage = (avg_users_count / max_users_count) * 100
        return percentage

    def get_purchase_percentage(self, product):
        groups = Group.objects.filter(product=product)
        if not len(groups):
            return 0
        groups_users_counts = [len(group.users.all()) for group in groups]
        all_users = User.objects.all()
        percentage = (sum(groups_users_counts) / len(all_users)) * 100
        return percentage


class LessonSerializer(serializers.ModelSerializer):
    product = serializers.HiddenField(default=CurrentProductDefault())

    class Meta:
        model = Lesson
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    product = serializers.HiddenField(default=CurrentProductDefault())

    class Meta:
        model = Group
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "username", "email", "date_joined")
