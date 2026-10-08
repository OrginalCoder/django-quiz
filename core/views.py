from django.views.generic import TemplateView
from django.http import HttpResponse
from quiz.models import Category
from leaderboard.models import UserScore


class LandingView(TemplateView):
    template_name = "core/landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()[:4]
        context["top_scores"] = UserScore.objects.select_related("user", "category").order_by("-score")[:3]
        context["total_categories"] = Category.objects.count()
        context["total_quizzes_taken"] = UserScore.objects.count()
        return context


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Allow: /",
        f"Sitemap: https://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    host = f"https://{request.get_host()}"
    urls = [
        f"{host}/",
        f"{host}/categories/",
        f"{host}/daily-challenge/",
        f"{host}/battle/",
        f"{host}/tournaments/",
        f"{host}/leaderboard/",
    ]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        xml.append(f"  <url><loc>{u}</loc><changefreq>daily</changefreq><priority>0.8</priority></url>")
    xml.append('</urlset>')
    return HttpResponse("\n".join(xml), content_type="application/xml")

