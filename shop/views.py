from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from .models import Product, Category, Order, OrderItem
from .serializers import ProductSerializer, CategorySerializer, OrderSerializer
from .filters import ProductFilter  


def home(request):
    return render(request, 'shop/home.html')


def orders_view(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'shop/orders.html', {'orders': orders})


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter  # min/max price + category filter
    search_fields = ["name", "description"]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Yeni sifariş yaradarkən:
        1. Məhsul stokunu yoxlayır
        2. Sifariş toplamını hesablayır
        3. Stock-dan məhsulu çıxır
        """
        order_items_data = self.request.data.get('items', [])
        if not order_items_data:
            raise ValueError("Order must have at least one item.")

        total = 0
        items_to_create = []

        # Stok yoxlaması və total hesablaması
        for item_data in order_items_data:
            product_id = item_data.get('product')
            quantity = int(item_data.get('quantity', 0))

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise ValueError(f"Product with id {product_id} does not exist.")

            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0.")

            if product.stock < quantity:
                raise ValueError(f"Not enough stock for product {product.name}. Available: {product.stock}")

            price = product.price * quantity
            total += price
            items_to_create.append({'product': product, 'quantity': quantity, 'price': product.price})

        # Sifarişi yarat
        order = serializer.save(user=self.request.user, total=total)

        # OrderItem-ları yarat və stokdan çıx
        for item in items_to_create:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )
            item['product'].stock -= item['quantity']
            item['product'].save()
