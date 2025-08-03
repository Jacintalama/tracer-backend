from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import TracerRecordViewSet
from .views import OCRParseView

router = DefaultRouter()
router.register(r'records', TracerRecordViewSet, basename='tracerrecord')

urlpatterns = [
    path('parse-image/', OCRParseView.as_view(), name='ocr-parse'),
    path('', include(router.urls)),
]
