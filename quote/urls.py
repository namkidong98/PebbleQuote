from django.urls import path
from .views import QuoteViewSet, QuoteLikeView, QuoteRegisterView, RecommendQuoteView
from .views import CommentView, CommentAdminView

# URL 패턴 정의
urlpatterns = [
    path('', QuoteViewSet.as_view({'get': 'list', 'post': 'create'}), name='quote-list'),
    path('<int:pk>/', QuoteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='quote-detail'),
    path('quote-register/', QuoteRegisterView.as_view(), name='quote-register'),
    path('<int:pk>/like/', QuoteLikeView.as_view(),name='quote-like'),
    path('<int:pk>/comment/',CommentView.as_view(),name='quote-comment'),
    path('comment/', CommentAdminView.as_view(), name='comment-admin'),
    path('recommend/', RecommendQuoteView.as_view(), name='recommend-quote'), # [POST] query에 대해 유사한 맥락의 명언 반환
]
