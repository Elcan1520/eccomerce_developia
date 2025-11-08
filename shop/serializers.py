from rest_framework import serializers
from .models import Product, Category, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemInputSerializer(many=True, write_only=True)
    order_items = OrderItemSerializer(source="items", many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "total", "status", "created_at", "items", "order_items"]
        read_only_fields = ["id", "user", "total", "status", "created_at", "order_items"]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Sifarişdə ən azı bir məhsul olmalıdır.")
        return value

    def create(self, validated_data):
        return Order.objects.create(user=self.context['request'].user)
