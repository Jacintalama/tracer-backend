from rest_framework import serializers
from .models import TracerRecord

class TracerRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TracerRecord
        fields = '__all__'
