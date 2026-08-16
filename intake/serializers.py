"""Serializers. Yours to write."""
from rest_framework import serializers

#Validates a single receipt.
class ReceiptSerializer(serializers.Serializer):
    client_uuid = serializers.UUIDField()

    outlet_code = serializers.CharField(
        max_length=16
    )

    invoice_no = serializers.CharField(
        max_length=50
    )

    method = serializers.ChoiceField(
        choices=[
            "CASH",
            "MPESA",
            "CHEQUE",
        ]
    )

    amount_kes = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    receipt_ref = serializers.CharField(
        max_length=50
    )

    recorded_at = serializers.DateTimeField()

    device_id = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True
    )

    def validate_amount_kes(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Amount must be greater than zero."
            )
        return value

#Validates the entire request.
class BatchSerializer(serializers.Serializer):

    device_id = serializers.CharField(
        max_length=50
    )

    receipts = ReceiptSerializer(
        many=True
    )

    def validate_receipts(self, receipts):

        if len(receipts) > 200:
            raise serializers.ValidationError(
                "A batch may contain at most 200 receipts."
            )

        if not receipts:
            raise serializers.ValidationError(
                "A batch must contain at least one receipt."
            )
        refs = [
        r["receipt_ref"]
        for r in receipts
        ]

        if len(refs) != len(set(refs)):
            raise serializers.ValidationError(
                "Duplicate receipt references detected."
            )

        return receipts
#for the list of collections get endpoint
from .models import Collection


class CollectionListSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Collection

        fields = [
            "receipt_ref",
            "client_uuid",
            "outlet_code",
            "invoice_no",
            "method",
            "amount_kes",
            "recorded_at",
            "receipt_device_id",
            "received_at",
        ]