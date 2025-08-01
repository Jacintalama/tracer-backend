from django.urls import path
from .views import OCRParseView

urlpatterns = [
    path('parse-image/', OCRParseView.as_view(), name='ocr-parse'),
]
