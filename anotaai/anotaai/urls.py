from django.urls import path
from marketplace.views import CategoryAPIView, ProductAPIView


urlpatterns = [
    path('api/category', CategoryAPIView.as_view(), name='category'),
    path('api/product', ProductAPIView.as_view(), name='product')
]