from django.views.generic import TemplateView
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
