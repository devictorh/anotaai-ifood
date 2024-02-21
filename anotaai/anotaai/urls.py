from django.urls import path
from marketplace.views import CategoryAPIView, ProductAPIView


urlpatterns = [
    path('api/category/', CategoryAPIView.as_view()),
    path('api/category/<str:category_id>', CategoryAPIView.as_view()),
    path('api/product/', ProductAPIView.as_view()),
    path('api/product/<str:product_id>', ProductAPIView.as_view())
]
