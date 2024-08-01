from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404

from database.database import vector_connect
from .models import Quote,User,Comment
from .serializers import QuoteSerializer,CommentSerializer

# 명언 전반에 대한 CRUD(w/o 인증 Token)
class QuoteViewSet(ModelViewSet):
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer

    def list(self, request):
        queryset = self.get_queryset().order_by('-like_count') # like_counts 기준 내림차순
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        data = {
            'content': request.data.get('content'),
            'description': request.data.get('description'),
            'author': request.data.get('author') # 원 발화자(유저랑 별개)
        }
        serializer = QuoteSerializer(data=data)
        if serializer.is_valid():
            quote_instance = serializer.save()

            # ChromaDB 연결해보고 연결되면 ChromaDB에도 삽입
            manager = vector_connect()
            if manager.connected:
                manager.add_quote(
                    description = quote_instance.description,
                    quote_id = quote_instance.id,
                    quote = quote_instance.content,
                    author = quote_instance.author,
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, partial=False):
        quote = get_object_or_404(Quote, pk=pk)
        serializer = self.get_serializer(quote, data=request.data, partial=partial)
        if serializer.is_valid():
            quote_instance = serializer.save()

            if ('content' in request.data) or ('description' in request.data) or ('author' in request.data):
                # ChromaDB에 업데이트(없애고 새로 만들기)
                manager = vector_connect()
                if manager.connected:
                    manager.delete_quote_by_quote_id(quote_id = quote_instance.id)
                    manager.add_quote(
                        description=quote_instance.description,
                        quote_id=quote_instance.id,
                        quote=quote_instance.content,
                        author=quote_instance.author,
                    )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        return self.update(request, pk, partial=True)

    def destroy(self, request, pk):
        quote = get_object_or_404(Quote, pk=pk)
        quote_id = quote.id # 삭제되고 나면 해당 객체의 id 추출이 안되기 때문에 미리 저장
        quote.delete() # PostgreSQL에서 삭제
        
        # ChromaDB에서 삭제
        manager = vector_connect()
        if manager.connected:
            manager.delete_quote_by_quote_id(quote_id=quote_id)

        return Response(status=status.HTTP_204_NO_CONTENT)


# 유저가 명언을 등록하는 경우(인증 Token 필요)
class QuoteRegisterView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        data = {
            'content': request.data.get('content'),
            'description': request.data.get('description'),
            'author': request.user.nickname,
            'user_author': request.user.id
        }
        serializer = QuoteSerializer(data=data)
        if serializer.is_valid():
            quote_instance = serializer.save()

            # ChromaDB 연결해보고 연결되면 ChromaDB에도 삽입
            manager = vector_connect()
            if manager.connected:
                manager.add_quote(
                    description = quote_instance.description,
                    quote_id = quote_instance.id,
                    quote = quote_instance.content,
                    author = quote_instance.author,
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

# 댓글 전체 조회 및 전체 삭제
class CommentAdminView(APIView):
    permission_classes = [AllowAny]  # 인증 불필요 -> 관리자용이기 때문, 이후에 IsAdminUser로 변경?

    def get(self, request):
        comment = Comment.objects.all()
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 서버 내부에서 scheduler를 설정해서 일정 시간에 해당 API를 호출해서 전체 Comment를 삭제하도록 구현 예정
    def delete(self, request):
        count, _ = Comment.objects.all().delete()
        return Response({"Message" : f"Deleted {count} comments."}, status=status.HTTP_204_NO_CONTENT)

class RecommendQuoteView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        try:
            query = request.data.get('query')
            if not query:
                return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            manager = vector_connect()
            retrieved_quotes = manager.search_quote(query=query, quote_num=3) # 3개의 상위 추천 Quote List
            data = []
            for retrieved_quote, relevance_score in retrieved_quotes: # relevance는 작아야 유사도가 높은 것
                data.append(
                    {
                        'author': retrieved_quote.metadata.get('author'),
                        'quote': retrieved_quote.metadata.get('quote'),
                        'description': retrieved_quote.page_content,
                        'score': relevance_score,
                    }
                )
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # # 게시물에 해당하는 단일 댓글 수정
    # def put(self, request, pk, comment_pk):
    #     comment = get_object_or_404(Comment, quote=pk, pk=comment_pk)
    #     serializer = CommentSerializer(comment, data=request.data)
    #     if serializer.is_valid():
    #         if request.user == comment.user:
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)