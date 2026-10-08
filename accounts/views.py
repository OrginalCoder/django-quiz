import os
import time
from datetime import date
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Sum, Avg, Count

from .forms import UzbekUserCreationForm, UzbekAuthenticationForm
from quiz.models import Category, UserMistake, DailyChallengeAttempt
from leaderboard.models import UserScore
from battle.models import BattleRoom
from .turnstile import verify_turnstile, get_client_ip


class RegisterView(CreateView):
    form_class = UzbekUserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["turnstile_site_key"] = os.environ.get("CLOUDFLARE_TURNSTILE_SITE_KEY", "")
        return context

    def form_valid(self, form):
        token = self.request.POST.get("cf-turnstile-response")
        if not verify_turnstile(token, get_client_ip(self.request)):
            form.add_error(None, "Xavfsizlik tekshiruvi (Captcha) muvaffaqiyatsiz bo'ldi. Qayta urinib ko'ring.")
            return self.form_invalid(form)
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Xush kelibsiz, {user.username}! Ro'yxatdan muvaffaqiyatli o'tdingiz.")
        return super().form_valid(form)


class UserLoginView(LoginView):
    form_class = UzbekAuthenticationForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["turnstile_site_key"] = os.environ.get("CLOUDFLARE_TURNSTILE_SITE_KEY", "")
        return context

    def dispatch(self, request, *args, **kwargs):
        lock_until = request.session.get("login_locked_until", 0)
        now = time.time()
        if lock_until and now < lock_until:
            wait_sec = int(lock_until - now)
            messages.error(request, f"Xavfsizlik: Ko'p marta xato urinishlar aniqlandi. Iltimos, {wait_sec} soniyadan keyin qayta urining.")
            return self.render_to_response(self.get_context_data(form=self.get_form()))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        token = self.request.POST.get("cf-turnstile-response")
        if not verify_turnstile(token, get_client_ip(self.request)):
            form.add_error(None, "Xavfsizlik tekshiruvi (Captcha) muvaffaqiyatsiz bo'ldi. Qayta urinib ko'ring.")
            return self.form_invalid(form)
        self.request.session["login_failed_attempts"] = 0
        self.request.session["login_locked_until"] = 0
        messages.success(self.request, f"Xush kelibsiz, {form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        attempts = self.request.session.get("login_failed_attempts", 0) + 1
        self.request.session["login_failed_attempts"] = attempts
        if attempts >= 5:
            self.request.session["login_locked_until"] = time.time() + 300
            messages.error(self.request, "Xavfsizlik: 5 marta xato parol kiritildi. Tizim 5 daqiqaga vaqtincha bloklandi.")
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("core:landing")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        user_scores = UserScore.objects.filter(user=user)
        total_score = user_scores.aggregate(total=Sum("score"))["total"] or 0
        quizzes_completed = user_scores.count()

        if quizzes_completed > 0:
            total_corr = sum(s.correct_answers for s in user_scores)
            total_quest = sum(s.total_questions for s in user_scores)
            avg_percent = round((total_corr / total_quest) * 100) if total_quest > 0 else 0
        else:
            avg_percent = 0

        unfinished_quiz = None
        quiz_sess = self.request.session.get("quiz_session")
        if quiz_sess and not quiz_sess.get("is_finished"):
            cat_slug = quiz_sess.get("category_slug")
            category = Category.objects.filter(slug=cat_slug).first()
            if category:
                curr_idx = quiz_sess.get("current_index", 0)
                q_ids = quiz_sess.get("question_ids", [])
                unfinished_quiz = {
                    "category": category,
                    "current_step": curr_idx + 1,
                    "total_questions": len(q_ids),
                    "score": quiz_sess.get("score", 0),
                    "slug": cat_slug,
                }

        categories_data = []
        for cat in Category.objects.all():
            cat_scores = user_scores.filter(category=cat)
            best_score = cat_scores.order_by("-score").first()
            best_percentage = best_score.percentage if best_score else None
            categories_data.append({
                "category": cat,
                "question_count": cat.questions.count(),
                "completed_count": cat_scores.count(),
                "best_score": best_score.score if best_score else 0,
                "best_percentage": best_percentage,
            })

        recent_activity = user_scores.select_related("category").order_by("-completed_at")[:8]
        unresolved_mistakes_count = UserMistake.objects.filter(user=user, is_resolved=False).count()
        today_attempt = DailyChallengeAttempt.objects.filter(user=user, challenge__date=date.today()).first()
        battles_won = BattleRoom.objects.filter(winner=user).count()

        from leaderboard.models import Badge, UserBadge, award_badges
        award_badges(user)
        user_badge_ids = set(UserBadge.objects.filter(user=user).values_list("badge_id", flat=True))
        all_badges = Badge.objects.all()
        badges_list = []
        for b in all_badges:
            is_unlocked = b.id in user_badge_ids
            ub = UserBadge.objects.filter(user=user, badge=b).first() if is_unlocked else None
            badges_list.append({
                "badge": b,
                "is_unlocked": is_unlocked,
                "earned_at": ub.earned_at if ub else None,
            })

        context.update({
            "total_score": total_score,
            "quizzes_completed": quizzes_completed,
            "average_percentage": avg_percent,
            "unfinished_quiz": unfinished_quiz,
            "categories_data": categories_data,
            "recent_activity": recent_activity,
            "unresolved_mistakes_count": unresolved_mistakes_count,
            "today_attempt": today_attempt,
            "battles_won": battles_won,
            "badges_list": badges_list,
            "earned_badges_count": len(user_badge_ids),
        })
        return context
