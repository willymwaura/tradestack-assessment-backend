"""Models for collection intake.

`Outlet` is given to you, complete, and is seeded by `make seed`.

Everything else is yours. There is deliberately no receipt model here - how
you store a receipt, what you make unique, and what you index are decisions we
want to see you make. Write down the reasoning in DECISIONS.md.
"""
from django.db import models


class Outlet(models.Model):
    outlet_code = models.CharField(max_length=16, primary_key=True)
    outlet_name = models.CharField(max_length=120)
    route_code = models.CharField(max_length=16, blank=True)

    class Meta:
        ordering = ["outlet_code"]

    def __str__(self):
        return f"{self.outlet_code} {self.outlet_name}"
