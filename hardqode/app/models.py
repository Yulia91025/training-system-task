from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Product(models.Model):
    title = models.CharField(max_length=255)
    cost = models.FloatField(validators=[MinValueValidator(0.0)])
    start_datetime = models.DateTimeField()
    min_group_students = models.PositiveIntegerField(default=1)
    max_group_students = models.PositiveIntegerField(default=10)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)


class Lesson(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Group(models.Model):
    name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    users = models.ManyToManyField(User)
