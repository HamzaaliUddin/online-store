from django.urls import path

from .views import BannerDetailView, BannerListCreateView, PublicBannerListView

app_name = "banners"

urlpatterns = [
    path("", BannerListCreateView.as_view(), name="banners"),
    path("<int:pk>/", BannerDetailView.as_view(), name="banner-detail"),
    path("public/", PublicBannerListView.as_view(), name="banners-public"),
]
