from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product
from .serializers import ProductSerializer, CategorySerializer
from bson import ObjectId


class CategoryAPIView(APIView):
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, category_id=None):
        if category_id:
            try:
                category = Category.objects.get(pk=ObjectId(category_id))
            except Category.DoesNotExist:
                return Response(
                    {"error": "Category not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = CategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_202_ACCEPTED
                )
            else:
                return Response(
                    serializer.data,
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, category_id=None):
        if category_id:
            try:
                category = Category.objects.get(pk=ObjectId(category_id))
                category.delete()

                return Response(
                    {"msg": "Category successfully deleted"},
                    status=status.HTTP_202_ACCEPTED
                )
            except Category.DoesNotExist:
                return Response(
                    {"error": "Category not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {"error": "It's necessary pass 'category_id'"},
                status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, category_id=None):
        if not category_id:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                category = Category.objects.get(pk=ObjectId(category_id))
                serializer = CategorySerializer(category)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Category.DoesNotExist:
                return Response(
                    {"erro": "Category not found"},
                    status=status.HTTP_404_NOT_FOUND
                )


class ProductAPIView(APIView):
    def post(self, request):
        category_id = request.data.get('category', None)
        if not category_id:
            return Response(
                {"error": "Category is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            category = Category.objects.get(
                pk=ObjectId(request.data['category'])
            )
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, product_id=None):
        category_id = request.data.get('category', None)
        if not category_id:
            return Response(
                {"error": "Category is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            category = Category.objects.get(pk=ObjectId(category_id))
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            product = Product.objects.get(pk=ObjectId(product_id))
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(product, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, product_id=None):
        try:
            product = Product.objects.get(pk=ObjectId(product_id))
            product.delete()

            return Response(
                {"msg": "Product successfully deleted"},
                status=status.HTTP_202_ACCEPTED
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, product_id=None):
        if not product_id:
            products = Product.objects.all()
            serializer = ProductSerializer(
                            products,
                            many=True,
                            context={'request': request}
                        )

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                product = Product.objects.get(pk=ObjectId(product_id))
                serializer = ProductSerializer(product)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Product.DoesNotExist:
                return Response(
                    {"erro": "Product not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
