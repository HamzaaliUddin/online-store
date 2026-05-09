from django.utils import timezone
from django.db.models import Q
from rest_framework import generics, permissions

from ecommerce.common.permissions import HasModulePermission

from .models import Banner
from .serializers import BannerSerializer


class BannerListCreateView(generics.ListCreateAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    module_code = "banners"
    filterset_fields = ["placement", "is_active"]
    search_fields = ["title", "subtitle"]
    ordering_fields = ["placement", "position", "created_at"]


class BannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    module_code = "banners"


class PublicBannerListView(generics.ListAPIView):
    """Public, customer-facing live banners."""

    permission_classes = [permissions.AllowAny]
    serializer_class = BannerSerializer
    filterset_fields = ["placement"]

    def get_queryset(self):
        now = timezone.now()
        return Banner.objects.filter(is_active=True).filter(
            (Q(starts_at__isnull=True) | Q(starts_at__lte=now))
            & (Q(ends_at__isnull=True) | Q(ends_at__gte=now))
        )
