"""Views for the collection intake API.

Two endpoints to build:

    POST /api/v1/collections/batch/
    GET  /api/v1/collections/

See README.md for the contract as it was handed over, and read
fixtures/sample_batch.json before you decide what the contract should
actually be.
"""
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import transaction

from rest_framework import status


from .models import CollectionBatch
from .models import BatchAudit

from .serializers import BatchSerializer

from .services import (
    generate_batch_hash,
    process_receipt,
)


class CollectionBatchView(APIView):

    def post(self, request):

        serializer = BatchSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        payload = serializer.validated_data

        batch_hash = generate_batch_hash(
            payload
        )

        existing_batch = (
            CollectionBatch.objects
            .filter(batch_hash=batch_hash)
            .first()
        )

        if existing_batch:

            BatchAudit.objects.create(
                batch=existing_batch,
                action=BatchAudit.Action.DUPLICATE_BATCH,
                details={},
            )

            return Response(
                {
                    "status": "duplicate_batch"
                },
                status=status.HTTP_200_OK
            )

        with transaction.atomic():

            batch = CollectionBatch.objects.create(
                device_id=payload["device_id"],
                batch_hash=batch_hash,
                receipt_count=len(
                    payload["receipts"]
                ),
            )

            created_count = 0
            updated_count = 0
            ignored_count = 0

            for receipt in payload["receipts"]:

                result = process_receipt(
                    receipt,
                    batch
                )

                if result == "created":
                    created_count += 1

                elif result == "updated":
                    updated_count += 1

                else:
                    ignored_count += 1

            BatchAudit.objects.create(
                batch=batch,
                action=BatchAudit.Action.PROCESSED,
                details={
                    "created": created_count,
                    "updated": updated_count,
                    "ignored": ignored_count,
                },
            )

        return Response(
            {
                "status": "processed",
                "batch_id": batch.id,
                "created": created_count,
                "updated": updated_count,
                "ignored": ignored_count,
            },
            status=status.HTTP_200_OK
        )


class CollectionListView(APIView):
    def get(self, request):
        raise NotImplementedError("GET /api/v1/collections/")
