from django.urls import path
from .views import QuoteViewSet, QuoteLikeView, QuoteRegisterView, RecommendQuoteView, QuoteUserView, QuoteAdminView
from .views import CommentView, CommentAdminView

# URL 패턴 정의
urlpatterns = [
    path('', QuoteViewSet.as_view({'get': 'list', 'post': 'create'}), name='quote-list'),
    path('<int:pk>/', QuoteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='quote-detail'),
    path('quote-register/', QuoteRegisterView.as_view(), name='quote-register'),
    path('<int:pk>/like/', QuoteLikeView.as_view(),name='quote-like'),          # [POST] 해당 Quote에 특정 유저가 좋아요 선택/해제 
    path('<int:pk>/comment/',CommentView.as_view(),name='quote-comment'),       # [GET] 해당 Quote에 달린 댓글 리스트 조회, [POST] 해당 Quote에 댓글 등록
    path('comment/', CommentAdminView.as_view(), name='comment-admin'),         # [GET] 전체 댓글 조회, [DELETE] 전체 댓글 삭제(초기화)
    path('recommend/', RecommendQuoteView.as_view(), name='recommend-quote'),   # [POST] query에 대해 유사한 맥락의 명언 반환
    path('<int:pk>/view/', QuoteUserView.as_view(), name='quote-viewed'),       # [POST] 특정 유저가 해당 Quote을 조회하였다는 기록
    path('view-clear/', QuoteAdminView.as_view(), name='view-clear'),           # [DELETE] 모든 Quote의 quote_viewers를 비움
]
