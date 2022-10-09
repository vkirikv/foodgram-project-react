from rest_framework.serializers import ModelSerializer

from recipes.models import Tag


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
