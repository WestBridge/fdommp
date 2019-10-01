from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from api import  serializers
from assets.models import *

class AssetsList(APIView):
    def get(self, request, format=None):
        snippets = Server.objects.all()
        serializer = serializers.AssetsServerSerializer(snippets, many=True)
        return Response(serializer.data)
    def post(self,request, format=None):
        data = request.data
        print ('request.data:',data)
        serializer = serializers.AssetsServerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(200)