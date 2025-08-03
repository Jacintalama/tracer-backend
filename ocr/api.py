# ocr/api.py

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import TracerRecord
from .serializers import TracerRecordSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # Skip CSRF checks entirely
        return


@method_decorator(csrf_exempt, name='dispatch')
class TracerRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD for TracerRecord, CSRF exempt so your client can DELETE without a token.
    """
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = []  # allow all for now
    queryset = TracerRecord.objects.all().order_by('-id')
    serializer_class = TracerRecordSerializer

    # (optional) override destroy to always return 204
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)
