# from django.contrib import admin
# from django.urls import path,include
# from .views import QuoteViewSet
# from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register(r'quotes', QuoteViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
# ]

from django.urls import path
from .views import QuoteViewSet

# URL 패턴 정의
urlpatterns = [
    path('quotes/', QuoteViewSet.as_view({'get': 'list', 'post': 'create'}), name='quote-list'),
    path('quotes/<int:pk>/', QuoteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='quote-detail'),
     path('quotes/<int:pk>/like/', QuoteViewSet.as_view({'post': 'like'}), name='quote-like'),  # like 액션 추가
   
]
