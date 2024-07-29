from django.urls import path
from .views import QuoteViewSet, QuoteLikeView,CommentView

# URL 패턴 정의
urlpatterns = [
    path('quotes/', QuoteViewSet.as_view({'get': 'list', 'post': 'create'}), name='quote-list'),
    path('quotes/<int:pk>/', QuoteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='quote-detail'),
    path('quotes/<int:pk>/like/', QuoteLikeView.as_view()),
    path('quotes/<int:pk>/comment/',CommentView.as_view()),
]
