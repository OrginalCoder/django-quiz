from django.urls import path
from .views import LandingView, robots_txt, sitemap_xml

app_name = "core"

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
]

