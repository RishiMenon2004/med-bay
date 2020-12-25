from django.urls import path
from . import views

app_name = 'pharma'
urlpatterns = [
    path("", views.shop, name="shop"),
    path("place", views.place, name="place"),
    path("bill_info", views.bill_info, name="bill_info"),
    path("remove", views.remove, name="remove"),
    path("add_one", views.add_one, name="add"),
    path("add_stock", views.add_stock, name="add_stock"),
    path("remove_stock", views.remove_stock, name="remove_stock"),
    path("bill", views.bill, name="bill"),
    path("cart", views.cart, name="cart"),
    path('bill_archive', views.bill_archive, name="bill_archive"),
    path("bill_archive_viewer", views.bill_archive_viewer, name="bill_archive_viewer"),
    path("order_prescription", views.order_prescription, name="order_prescription"),
    path("edit_prescription", views.edit_prescription, name="edit_prescription")
]
