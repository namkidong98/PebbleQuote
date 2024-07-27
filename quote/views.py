

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import Quote
from .serializers import QuoteSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
# from .db_utils import vector_connect




class QuoteViewSet(ModelViewSet):
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
    
    
    @action(detail=True, methods=['post'],permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        quote = self.get_object()
        user = request.user

        # 이미 좋아요를 누른 경우
        if quote.liked_by.filter(id=user.id).exists():
            return Response({"detail": "You have already liked this quote."}, status=status.HTTP_400_BAD_REQUEST)

        # 좋아요 추가
        quote.liked_by.add(user)
        quote.like_count = quote.liked_by.count()  # 좋아요 개수 업데이트
        quote.save()
        
        return Response({"detail": "Quote liked successfully!", "like_count": quote.like_count}, status=status.HTTP_200_OK)
