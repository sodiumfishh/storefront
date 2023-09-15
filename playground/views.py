from django.shortcuts import render
from django.db.models import Q, F
from django.db.models.aggregates import Count, Sum
from store.models import Order, OrderItem, Product, Customer, Collection


def say_hello(request):
    ###### Q objects ######
    # queryset = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20))

    ###### F objects #####
    # queryset = Product.objects.filter(inventory=F("unit_price"))

    # queryset = (
    #     Product.objects.filter(id__in=OrderItem.objects.values("product_id").distinct())
    #     .order_by("title")
    #     .values("title")
    # )

    ## Select_related
    # queryset = Product.objects.select_related("collection").all()

    """
    prefetch_related
    """
    # queryset = (
    #     Product.objects.prefetch_related("promotions")
    #     .select_related("collection")
    #     .all()
    # )

    # queryset = (
    #     Order.objects.select_related("customer")
    #     .prefetch_related("orderitem_set__product")
    #     .order_by("-placed_at")[:5]
    # )

    # # result = Order.objects.filter(customer__id=1).aggregate(Count("id"))

    # query = Order.objects.annotate(total_price=Sum("orderitem__unit_price"))

    # list_query = list(query)

    # queryset = Product.objects.prefetch_related("collection").all()

    # context = {
    #     "name": "Mosh",
    #     # "customers": list(customer_queryset),
    #     "products": list(queryset),
    # }

    return render(request, "hello.html", context)
