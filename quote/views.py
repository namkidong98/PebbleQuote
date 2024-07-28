

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import Quote,User
from .serializers import QuoteSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
# from .db_utils import vector_connect




class QuoteViewSet(ModelViewSet):
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
    
    
    
class QuoteLikeView(APIView):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, pk):
        # 현재 명언
        quote = get_object_or_404(Quote, pk=pk)
        # 현재 유저
        profile = get_object_or_404(User, id=request.user.id)
        # 해당 명언 좋아요 유무 파악
        check_like_quote = profile.like_quotes.filter(id=pk)

        if check_like_quote.exists():
            profile.like_quotes.remove(quote)  # 현재 유저의 좋아요한 명언 목록에서 현재 명언 제거
            quote.like_count -= 1  # 현재 명언의 좋아요 개수 하향
            quote.save()
            return Response('이미 선택하여 제거되었습니다', status=status.HTTP_200_OK)
        else:
            profile.like_quotes.add(quote)  # 현재 유저의 좋아요한 명언 목록에 현재 명언 추가
            quote.like_count += 1  # 현재 명언의 좋아요 개수 상향
            quote.save()
            return Response('추가되었습니다', status=status.HTTP_200_OK)
