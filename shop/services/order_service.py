from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from ..models import Product, Order, OrderItem

class OrderProcessingError(Exception):
    pass

def create_order(user, items_data, shipping_address=None):
    if not items_data:
        raise OrderProcessingError("Sifarişdə ən azı bir məhsul olmalıdır.")

    with transaction.atomic():
        order = Order.objects.create(user=user, total=Decimal('0'), status='pending')

        total = Decimal('0')
        for item in items_data:
            product_id = item.get("product_id") or item.get("product")
            qty = int(item.get("quantity", 0))
            if qty <= 0:
                raise OrderProcessingError("Miqdar 0-dən böyük olmalıdır.")

            try:
                product = Product.objects.get(pk=product_id)
            except ObjectDoesNotExist:
                raise OrderProcessingError(f"Məhsul (id={product_id}) tapılmadı.")

            product.reduce_stock(qty)

            line_total = product.price * qty
            total += line_total

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=product.price
            )

        order.total = total
        order.status = 'completed'
        order.save(update_fields=['total', 'status'])
        return order
