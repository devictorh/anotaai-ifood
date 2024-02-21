from rest_framework import serializers
from .models import Category, Product
from bson import ObjectId


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'request' in self.context \
           and self.context['request'].method == 'GET':
            self.fields['category'] = serializers.SerializerMethodField(
                read_only=True,
                source='get_category'
            )

    class Meta:
        model = Product
        fields = '__all__'

    def get_category(self, obj):
        try:
            id = obj.category
            category_data = Category.objects.get(pk=ObjectId(id))
            serializer = CategorySerializer(category_data)
            return serializer.data
        except Category.DoesNotExist:
            return None
