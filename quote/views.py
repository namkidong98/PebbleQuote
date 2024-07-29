from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import Quote,User,Comment
from .serializers import QuoteSerializer,CommentSerializer
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

class CommentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly] # GET 요청과 같은 안전한(read-only) 메소드에 대해서는 인증 없이 접근 허용

    # 게시물에 해당하는 전체 댓글 조회
    def get(self, request, pk):
        comment = Comment.objects.filter(quote=pk)  
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 게시물에 해당하는 댓글 생성
    def post(self, request, pk):
        comment = Comment()
        comment.content = request.POST['content']
        comment.quote = Quote(id=pk)
        comment.user = request.user
        comment.save()
        return Response(data="생성되었습니다", status=status.HTTP_200_OK)

    # # 게시물에 해당하는 단일 댓글 수정
    # def put(self, request, pk, comment_pk):
    #     comment = get_object_or_404(Comment, quote=pk, pk=comment_pk)
    #     serializer = CommentSerializer(comment, data=request.data)
    #     if serializer.is_valid():
    #         if request.user == comment.user:
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)