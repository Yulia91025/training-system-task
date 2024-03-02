from django.urls import path, include
from .views import ProductsViewSet, LessonViewSet, GroupViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"products", ProductsViewSet, basename="products")
router.register(r"products/(?P<id>[^/.]+)/lessons", LessonViewSet, basename="lessons")
router.register(r"products/(?P<id>[^/.]+)/groups", GroupViewSet, basename="groups")

urlpatterns = [
    path("", include(router.urls)),
]
