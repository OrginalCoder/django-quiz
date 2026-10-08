import io
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from django.db.models import Sum, Count, Max
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from .models import UserScore
from quiz.models import Category


class ResultView(LoginRequiredMixin, DetailView):
    model = UserScore
    pk_url_kwarg = "score_id"
    template_name = "leaderboard/result.html"
    context_object_name = "score_record"
    login_url = "accounts:login"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Siz faqat o'zingizning natijangizni ko'rishingiz mumkin.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        score = self.object

        percentage = score.percentage
        if percentage >= 90:
            feedback_message = "Ajoyib natija! Siz haqiqiy Django mutaxassisisiz!"
            feedback_level = "excellent"
        elif percentage >= 70:
            feedback_message = "Yaxshi natija! Bilimlaringiz mustahkam, biroz takrorlash kifoya."
            feedback_level = "good"
        elif percentage >= 50:
            feedback_message = "Qoniqarli natija. Mavzularni yana bir bor ko'rib chiqishingizni tavsiya qilamiz."
            feedback_level = "fair"
        else:
            feedback_message = "Xafa bo'lmang! Xatolardan o'rganib, yana bir bor urinib ko'ring."
            feedback_level = "poor"

        context.update({
            "percentage": percentage,
            "feedback_message": feedback_message,
            "feedback_level": feedback_level,
            "answers_breakdown": score.details or [],
            "category": score.category,
            "is_certificate_eligible": percentage >= 85,
        })
        return context


class CertificateDownloadView(LoginRequiredMixin, View):
    def get(self, request, score_id):
        score = get_object_or_404(UserScore, id=score_id)
        if score.user != request.user and not request.user.is_staff:
            raise PermissionDenied("Siz faqat o'zingizning sertifikatingizni yuklab olishingiz mumkin.")

        if score.percentage < 85:
            messages.warning(request, "Sertifikat faqat 85% dan yuqori natijalar uchun beriladi.")
            return redirect("leaderboard:result", score_id=score.id)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=landscape(letter))
        width, height = landscape(letter)

        p.setFillColor(colors.HexColor("#0f0c29"))
        p.rect(0, 0, width, height, fill=True, stroke=False)

        p.setStrokeColor(colors.HexColor("#ffd166"))
        p.setLineWidth(4)
        p.rect(25, 25, width - 50, height - 50)

        p.setStrokeColor(colors.HexColor("#ffffff"))
        p.setLineWidth(1)
        p.rect(33, 33, width - 66, height - 66)

        corner_len = 30
        p.setStrokeColor(colors.HexColor("#ffd166"))
        p.setLineWidth(3)

        p.line(40, height - 40, 40 + corner_len, height - 40)
        p.line(40, height - 40, 40, height - 40 - corner_len)

        p.line(width - 40, height - 40, width - 40 - corner_len, height - 40)
        p.line(width - 40, height - 40, width - 40, height - 40 - corner_len)

        p.line(40, 40, 40 + corner_len, 40)
        p.line(40, 40, 40, 40 + corner_len)

        p.line(width - 40, 40, width - 40 - corner_len, 40)
        p.line(width - 40, 40, width - 40, 40 + corner_len)

        p.setFillColor(colors.HexColor("#ffd166"))
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width / 2, height - 85, "DJANGO QUIZ & LEADERBOARD PLATFORMASI")

        p.setFont("Helvetica-Bold", 32)
        p.setFillColor(colors.HexColor("#ffffff"))
        p.drawCentredString(width / 2, height - 135, "DJANGO SERTIFIKATI")

        p.setFont("Helvetica", 13)
        p.setFillColor(colors.HexColor("#a9a3c9"))
        p.drawCentredString(width / 2, height - 170, "Ushbu sertifikat Django bo'yicha yuqori bilim darajasini isbotladi:")

        student_name = score.user.username.upper()
        p.setFont("Helvetica-Bold", 28)
        p.setFillColor(colors.HexColor("#ffd166"))
        p.drawCentredString(width / 2, height - 225, student_name)

        p.setStrokeColor(colors.HexColor("#ffd166"))
        p.setLineWidth(1.5)
        p.line(width / 2 - 160, height - 235, width / 2 + 160, height - 235)

        cat_name = score.category.name if score.category else "Umumiy Django Viktorinasi"
        p.setFont("Helvetica", 14)
        p.setFillColor(colors.HexColor("#f2f0fa"))
        p.drawCentredString(width / 2, height - 275, f"Yo'nalish: {cat_name}")

        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(colors.HexColor("#4ade80"))
        p.drawCentredString(width / 2, height - 310, f"Natija: {score.score} ball ({score.percentage}% to'g'ri javob)")

        p.setFont("Helvetica", 11)
        p.setFillColor(colors.HexColor("#a9a3c9"))
        cert_id = f"CERT-DJ-{score.id:05d}"
        p.drawString(60, 75, f"Sertifikat raqami: {cert_id}")
        p.drawString(60, 58, f"Berilgan sana: {score.completed_at.strftime('%d.%m.%Y')}")

        p.drawRightString(width - 60, 75, "Rasmiy verifikatsiya: TASDIQLANGAN")
        p.drawRightString(width - 60, 58, "djangoquiz.uz/leaderboard/")

        p.showPage()
        p.save()

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"Django_Sertifikat_{score.user.username}_{score.id}.pdf")


class LeaderboardView(ListView):
    model = UserScore
    template_name = "leaderboard/leaderboard.html"
    context_object_name = "scores"
    paginate_by = 20

    def get_queryset(self):
        category_slug = self.request.GET.get("category")
        qs = UserScore.objects.select_related("user", "category")

        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        return qs.order_by("-score", "-completed_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.request.GET.get("category", "")

        context["categories"] = Category.objects.all()
        context["selected_category_slug"] = category_slug
        selected_category = Category.objects.filter(slug=category_slug).first() if category_slug else None
        context["selected_category"] = selected_category

        base_qs = self.get_queryset()
        top_3 = list(base_qs[:3])
        context["top_1"] = top_3[0] if len(top_3) > 0 else None
        context["top_2"] = top_3[1] if len(top_3) > 1 else None
        context["top_3"] = top_3[2] if len(top_3) > 2 else None
        context["has_podium"] = len(top_3) > 0

        if self.request.user.is_authenticated:
            user_scores = base_qs.filter(user=self.request.user)
            context["user_best_score"] = user_scores.first()
            if context["user_best_score"]:
                higher_scores_count = base_qs.filter(score__gt=context["user_best_score"].score).count()
                context["user_rank"] = higher_scores_count + 1

        return context
