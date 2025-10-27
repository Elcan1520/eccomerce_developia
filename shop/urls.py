from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, OrderViewSet, orders_view

# DRF router
router = DefaultRouter()
router.register("products", ProductViewSet, basename="products")
router.register("categories", CategoryViewSet, basename="categories")
router.register("orders", OrderViewSet, basename="orders")

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),

    # Custom front-end pages
    path("orders/", orders_view, name="orders"),
]