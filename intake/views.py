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
from django.utils.dateparse import parse_date

from django.db import transaction

from rest_framework import status

from .models import Collection
from .models import CollectionBatch
from .models import BatchAudit
from .serializers import CollectionListSerializer
from .pagination import CollectionPagination

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

            receipt_results = []

            for receipt in payload["receipts"]:

                result = process_receipt(
                    receipt,
                    batch
                )
                receipt_results.append(result)

                if result["status"] == "created":
                    created_count += 1

                elif result["status"] == "updated":
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
        "receipts": receipt_results,
    },
    status=status.HTTP_200_OK
)


class CollectionListView(APIView):

    def get(self, request):

        queryset = Collection.objects.all()

        outlet_code = request.GET.get(
            "outlet_code"
        )

        if outlet_code:
            queryset = queryset.filter(
                outlet_code=outlet_code
            )

        date_from = request.GET.get(
            "date_from"
        )

        if date_from:
            queryset = queryset.filter(
                recorded_at__date__gte=parse_date(
                    date_from
                )
            )

        date_to = request.GET.get(
            "date_to"
        )

        if date_to:
            queryset = queryset.filter(
                recorded_at__date__lte=parse_date(
                    date_to
                )
            )

        paginator = CollectionPagination()

        page = paginator.paginate_queryset(
            queryset,
            request
        )

        serializer = CollectionListSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )
