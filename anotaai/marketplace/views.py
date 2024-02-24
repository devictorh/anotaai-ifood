import boto3
import os
import json
import logging

from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product
from .serializers import ProductSerializer, CategorySerializer
from bson import ObjectId

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
AWS_URL_SQS = os.getenv('AWS_URL_SQS')
AWS_SNS_ARN = os.getenv('AWS_SNS_ARN')


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
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.message: dict = {}
        self.sns = boto3.client(
            "sns",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

    def _send_notification_to_sns_topic(self, message):
        try:
            response = self.sns.publish(
                TopicArn=AWS_SNS_ARN,
                Message=json.dumps(message)
            )
            logging.info("notification sent successfully")
        except Exception as err:
            logging.error(f"error sending message: {err}")

    def post(self, request):
        category_id = request.data.get('category', None)
        if not category_id:
            return Response(
                {"error": "Category is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            category = Category.objects.get(pk=ObjectId(category_id))
            category_data = CategorySerializer(category)
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            self.message["type"] = "create"
            self.message["product"] = serializer.data
            self.message["product"]['category'] = category_data.data
            self._send_notification_to_sns_topic(self.message)

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
            category_data = CategorySerializer(category)
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

            self.message["type"] = "update"
            self.message["product"] = serializer.data
            self.message["product"]['category'] = category_data.data
            self._send_notification_to_sns_topic(self.message)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, product_id=None):
        try:
            product = Product.objects.get(pk=ObjectId(product_id))
            product_data = ProductSerializer(product)
            if product:
                product.delete()

                self.message["type"] = "delete"
                self.message['product'] = product_data
                self._send_notification_to_sns_topic(self.message)

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
