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


class CollectionBatchView(APIView):
    def post(self, request):
        raise NotImplementedError("POST /api/v1/collections/batch/")


class CollectionListView(APIView):
    def get(self, request):
        raise NotImplementedError("GET /api/v1/collections/")
