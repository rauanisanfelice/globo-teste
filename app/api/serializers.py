from rest_framework import serializers

from pipeline.models import Audiencia, TempoDisponivel


class AudienciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audiencia
        fields = [
            "signal",
            "program_code",
            "exhibition_date",
            "program_start_time",
            "average_audience",
        ]


class TempoDisponivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempoDisponivel
        fields = ["signal", "program_code", "date", "available_time"]


class DetailField(serializers.DictField):

    mean = serializers.DecimalField(max_digits=15, decimal_places=2)
    median = serializers.DecimalField(max_digits=15, decimal_places=2)
    sum = serializers.DecimalField(max_digits=15, decimal_places=2)
    max = serializers.DecimalField(max_digits=15, decimal_places=2)
    min = serializers.DecimalField(max_digits=15, decimal_places=2)


class ResponseSerializer(serializers.Serializer):

    signal = serializers.CharField(required=True, allow_blank=False, max_length=10)
    program_code = serializers.CharField(
        required=True, allow_blank=False, max_length=10
    )
    weekday = serializers.IntegerField()
    available_time = DetailField()
    predicted_audience = DetailField()
