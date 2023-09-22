from typing import Any
from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode

from tags.models import TaggedItem
from .models import Collection, Customer, Order, OrderItem, Product


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"

    # Used in the url queryset. For example: `example.com/?inventory=`
    parameter_name = "inventory"

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            ("<10", "Low"),
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


class TagInline(GenericTabularInline):
    autocomplete_fields = ["tag"]
    model = TaggedItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ["collection"]
    prepopulated_fields = {"slug": ["title"]}
    actions = ["clear_inventory"]
    inlines = [TagInline]
    list_display = [
        "title",
        "unit_price",
        "inventory_status",
        "collection_title",
    ]
    list_editable = ["unit_price"]
    list_filter = ["collection", "last_update", InventoryFilter]
    list_per_page = 10
    list_select_related = ["collection"]
    search_fields = ["title"]

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        if product.inventory < 10:
            return "Low"
        return "OK"

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset: QuerySet):
        updated_count = queryset.update(
            inventory=0
        )  # returns number of updated records
        self.message_user(
            request,
            f"{updated_count} products were successfully updated",
            messages.SUCCESS,
        )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name"]
    list_display = ["first_name", "last_name", "membership", "orders_count"]
    list_editable = ["membership"]
    list_per_page = 10
    ordering = ["first_name", "last_name"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    def orders_count(self, customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": str(customer.id)})
        )
        return format_html("<a href='{}'>{}</a>", url, customer.orders_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(orders_count=Count("order"))


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ["product"]
    model = OrderItem
    min_num = 1
    max_num = 10


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ["customer"]
    inlines = [OrderItemInline]
    list_display = ["id", "placed_at", "customer", "items_count"]

    def items_count(self, order):
        url = (
            reverse("admin:store_orderitem_changelist")
            + "?"
            + urlencode({"order__id": order.id})
        )
        return format_html("<a href='{}'>{}</a>", url, order.items_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(items_count=Count("orderitem"))


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "products_count"]
    search_fields = ["title"]

    @admin.display(ordering="products_count")  # Telling django which column to sort by
    def products_count(self, collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )
        return format_html("<a href='{}'>{}</a>", url, collection.products_count)
        # return collection.products_count

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count=Count("product"))


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["product", "quantity", "unit_price"]
