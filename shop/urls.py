from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, OrderViewSet, orders_view


router = DefaultRouter()
router.register("products", ProductViewSet, basename="products")
router.register("categories", CategoryViewSet, basename="categories")
router.register("orders", OrderViewSet, basename="orders")

urlpatterns = [
   
    path("api/", include(router.urls)),

    
    path("orders/", orders_view, name="orders"),
]