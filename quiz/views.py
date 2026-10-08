import json
import random
import time
from datetime import date
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .models import Category, Question, Choice, UserMistake, DailyChallenge, DailyChallengeAttempt
from .signals import quiz_completed


class CategoryListView(ListView):
    model = Category
    template_name = "quiz/category_list.html"
    context_object_name = "categories"


class CategoryDetailView(DetailView):
    model = Category
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "quiz/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = self.object.questions.all()
        context["total_questions"] = questions.count()
        context["easy_count"] = questions.filter(difficulty="easy").count()
        context["medium_count"] = questions.filter(difficulty="medium").count()
        context["hard_count"] = questions.filter(difficulty="hard").count()
        return context


class QuizView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Viktorinada qatnashish uchun tizimga kiring")
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, category_slug):
        category = get_object_or_404(Category, slug=category_slug)
        questions = list(category.questions.all().order_by("id"))

        if not questions:
            messages.error(request, "Bu kategoriyada hali savollar mavjud emas.")
            return redirect("quiz:category_detail", slug=category.slug)

        sess = request.session.get("quiz_session", {})
        restart = request.GET.get("restart") == "1"

        if restart or sess.get("category_slug") != category.slug or sess.get("is_finished"):
            question_ids = [q.id for q in questions]
            random.shuffle(question_ids)
            request.session["quiz_session"] = {
                "category_slug": category.slug,
                "category_id": category.id,
                "question_ids": question_ids,
                "current_index": 0,
                "score": 0,
                "correct_count": 0,
                "answers": [],
                "is_finished": False,
            }
            request.session["quiz_rnd_seed"] = random.randint(1, 1000000)
            request.session.modified = True

        return render(request, "quiz/quiz_screen.html", {
            "category": category,
            "total_questions": len(questions),
        })


class QuizQuestionApiView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Avtorizatsiyadan o'tilmagan"}, status=401)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, category_slug):
        sess = request.session.get("quiz_session")
        if not sess or sess.get("category_slug") != category_slug:
            return JsonResponse({"error": "Sessiya topilmadi"}, status=404)

        current_index = sess.get("current_index", 0)
        question_ids = sess.get("question_ids", [])

        if current_index >= len(question_ids):
            return JsonResponse({"is_finished": True})

        question_id = question_ids[current_index]
        question = get_object_or_404(
            Question.objects.prefetch_related("choices"), id=question_id
        )

        seed_val = request.session.setdefault("quiz_rnd_seed", random.randint(1, 1000000))
        rng = random.Random(f"{seed_val}_{question_id}")
        choices = list(question.choices.all())
        rng.shuffle(choices)

        letters = ["A", "B", "C", "D", "E"]
        choices_data = []
        for idx, ch in enumerate(choices):
            choices_data.append({
                "id": ch.id,
                "text": ch.text,
                "badge": letters[idx] if idx < len(letters) else str(idx + 1)
            })

        sess["question_start_time"] = time.time()
        request.session.modified = True

        return JsonResponse({
            "is_finished": False,
            "question_id": question.id,
            "text": question.text,
            "difficulty": question.difficulty,
            "difficulty_display": question.get_difficulty_display(),
            "points": question.points,
            "current_index": current_index + 1,
            "total_questions": len(question_ids),
            "score": sess.get("score", 0),
            "choices": choices_data,
            "code_snippet": question.code_snippet,
            "question_type": question.question_type,
        })


class QuizAnswerApiView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Avtorizatsiyadan o'tilmagan"}, status=401)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, category_slug):
        sess = request.session.get("quiz_session")
        if not sess or sess.get("category_slug") != category_slug:
            return JsonResponse({"error": "Sessiya topilmadi"}, status=404)

        try:
            body = json.loads(request.body)
            question_id = int(body.get("question_id"))
            choice_id = int(body.get("choice_id")) if body.get("choice_id") is not None else None
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({"error": "Noto'g'ri ma'lumot formati"}, status=400)

        current_index = sess.get("current_index", 0)
        question_ids = sess.get("question_ids", [])

        if current_index >= len(question_ids) or question_ids[current_index] != question_id:
            return JsonResponse({"error": "Noto'g'ri savol ketma-ketligi"}, status=400)

        start_time = sess.get("question_start_time")
        if start_time and not settings.DEBUG and not getattr(settings, 'TESTING', False):
            elapsed = time.time() - start_time
            if elapsed < 0.35:
                return JsonResponse({"error": "Javob berish tezligi g'ayritabiiy yuqori"}, status=400)
        sess["question_start_time"] = None

        question = get_object_or_404(Question, id=question_id)
        choices = list(question.choices.all())
        correct_choice = next((c for c in choices if c.is_correct), None)
        selected_choice = next((c for c in choices if c.id == choice_id), None) if choice_id else None

        is_correct = bool(selected_choice and selected_choice.is_correct)
        points_earned = question.points if is_correct else 0

        sess["score"] = sess.get("score", 0) + points_earned
        if is_correct:
            sess["correct_count"] = sess.get("correct_count", 0) + 1
            UserMistake.objects.filter(user=request.user, question=question).update(is_resolved=True)
            from leaderboard.models import award_badges
            award_badges(request.user)
        else:
            UserMistake.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={"selected_choice": selected_choice, "is_resolved": False}
            )

        sess.setdefault("answers", []).append({
            "question_id": question.id,
            "question_text": question.text,
            "difficulty": question.difficulty,
            "difficulty_display": question.get_difficulty_display(),
            "points": question.points,
            "points_earned": points_earned,
            "selected_choice_id": choice_id,
            "selected_choice_text": selected_choice.text if selected_choice else "Javob berilmadi",
            "correct_choice_id": correct_choice.id if correct_choice else None,
            "correct_choice_text": correct_choice.text if correct_choice else "",
            "is_correct": is_correct,
        })

        sess["current_index"] = current_index + 1
        is_finished = sess["current_index"] >= len(question_ids)

        next_url = None
        if is_finished:
            sess["is_finished"] = True
            category = Category.objects.filter(slug=category_slug).first()

            signal_responses = quiz_completed.send(
                sender=self.__class__,
                user=request.user,
                category=category,
                score=sess["score"],
                total_questions=len(question_ids),
                correct_answers=sess.get("correct_count", 0),
                details=sess.get("answers", []),
            )

            user_score_id = None
            for receiver, response in signal_responses:
                if response and hasattr(response, "id"):
                    user_score_id = response.id
                    break

            if user_score_id:
                next_url = reverse("leaderboard:result", kwargs={"score_id": user_score_id})
            else:
                next_url = reverse("accounts:dashboard")

            from leaderboard.models import award_badges
            award_badges(request.user)

        request.session.modified = True

        return JsonResponse({
            "is_correct": is_correct,
            "correct_choice_id": correct_choice.id if correct_choice else None,
            "selected_choice_id": choice_id,
            "points_earned": points_earned,
            "running_score": sess["score"],
            "is_finished": is_finished,
            "next_url": next_url,
        })


class MistakesListView(LoginRequiredMixin, TemplateView):
    template_name = "quiz/mistakes_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unresolved_mistakes = UserMistake.objects.filter(
            user=self.request.user, is_resolved=False
        ).select_related("question", "question__category", "selected_choice")
        resolved_count = UserMistake.objects.filter(user=self.request.user, is_resolved=True).count()
        context["mistakes"] = unresolved_mistakes
        context["unresolved_count"] = unresolved_mistakes.count()
        context["resolved_count"] = resolved_count
        return context


class MistakesPracticeView(LoginRequiredMixin, View):
    def get(self, request):
        mistakes = list(UserMistake.objects.filter(user=request.user, is_resolved=False).select_related("question"))
        if not mistakes:
            messages.info(request, "Ajoyib! Sizda hozircha to'g'rilanmagan xatolar mavjud emas.")
            return redirect("accounts:dashboard")

        question_ids = [m.question_id for m in mistakes]
        random.shuffle(question_ids)

        dummy_category, _ = Category.objects.get_or_create(
            slug="xatolar",
            defaults={"name": "Xatolar ustida ishlash", "icon": "file-text", "description": "Oldin xato qilingan savollar"}
        )

        request.session["quiz_session"] = {
            "category_slug": "xatolar",
            "category_id": dummy_category.id,
            "question_ids": question_ids,
            "current_index": 0,
            "score": 0,
            "correct_count": 0,
            "answers": [],
            "is_finished": False,
        }
        request.session["quiz_rnd_seed"] = random.randint(1, 1000000)
        request.session.modified = True

        return render(request, "quiz/quiz_screen.html", {
            "category": dummy_category,
            "total_questions": len(question_ids),
        })


def get_today_challenge():
    today = date.today()
    challenge = DailyChallenge.objects.filter(date=today).first()
    if not challenge:
        question = Question.objects.order_by("?").first()
        if question:
            challenge = DailyChallenge.objects.create(
                date=today,
                question=question,
                bonus_points=5
            )
    return challenge


class DailyChallengeView(TemplateView):
    template_name = "quiz/daily_challenge.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        challenge = get_today_challenge()
        context["challenge"] = challenge

        if challenge:
            letters = ["A", "B", "C", "D", "E"]
            choices = list(challenge.question.choices.all())
            choices_data = []
            for idx, ch in enumerate(choices):
                choices_data.append({
                    "id": ch.id,
                    "text": ch.text,
                    "badge": letters[idx] if idx < len(letters) else str(idx + 1)
                })
            context["choices"] = choices_data

            if self.request.user.is_authenticated:
                user_attempt = DailyChallengeAttempt.objects.filter(
                    user=self.request.user, challenge=challenge
                ).first()
                context["user_attempt"] = user_attempt
                context["has_attempted"] = bool(user_attempt)
        return context


class DailyChallengeAnswerApiView(LoginRequiredMixin, View):
    def post(self, request):
        challenge = get_today_challenge()
        if not challenge:
            return JsonResponse({"error": "Bugungi savol topilmadi"}, status=404)

        if DailyChallengeAttempt.objects.filter(user=request.user, challenge=challenge).exists():
            return JsonResponse({"error": "Siz bugungi savolga allaqachon javob bergansiz"}, status=400)

        try:
            body = json.loads(request.body)
            choice_id = int(body.get("choice_id"))
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({"error": "Noto'g'ri ma'lumot formati"}, status=400)

        choices = list(challenge.question.choices.all())
        selected_choice = next((c for c in choices if c.id == choice_id), None)
        correct_choice = next((c for c in choices if c.is_correct), None)

        if not selected_choice:
            return JsonResponse({"error": "Tanlangan variant topilmadi"}, status=404)

        is_correct = selected_choice.is_correct

        DailyChallengeAttempt.objects.create(
            user=request.user,
            challenge=challenge,
            selected_choice=selected_choice,
            is_correct=is_correct,
        )

        from leaderboard.services import record_user_score
        if is_correct:
            record_user_score(
                user=request.user,
                category=challenge.question.category,
                score=challenge.bonus_points,
                total_questions=1,
                correct_answers=1,
                details=[{
                    "question_text": challenge.question.text,
                    "difficulty": challenge.question.difficulty,
                    "difficulty_display": challenge.question.get_difficulty_display(),
                    "points": challenge.bonus_points,
                    "points_earned": challenge.bonus_points,
                    "selected_choice_text": selected_choice.text,
                    "correct_choice_text": correct_choice.text if correct_choice else "",
                    "is_correct": True,
                }]
            )
            from leaderboard.models import award_badges
            award_badges(request.user)

        return JsonResponse({
            "is_correct": is_correct,
            "correct_choice_id": correct_choice.id if correct_choice else None,
            "bonus_points": challenge.bonus_points if is_correct else 0,
        })


class AiExplainApiView(LoginRequiredMixin, View):
    def get(self, request, question_id):
        last_req = request.session.get("last_ai_time")
        now = time.time()
        if last_req and not settings.DEBUG and not getattr(settings, 'TESTING', False) and (now - last_req) < 2.0:
            return JsonResponse({"error": "So'rovlar juda tez yuborilmoqda, iltimos kuting"}, status=429)
        request.session["last_ai_time"] = now
        request.session.modified = True

        question = get_object_or_404(
            Question.objects.prefetch_related("choices", "category"), id=question_id
        )
        correct_choice = next((c for c in question.choices.all() if c.is_correct), None)
        correct_text = correct_choice.text if correct_choice else ""

        explanation_text = question.explanation
        if not explanation_text:
            explanation_text = (
                f"Ushbu savol '{question.category.name}' bo'limiga tegishli. "
                f"To'g'ri javob: '{correct_text}'. "
                f"Django arxitekturasida ushbu usul eng to'g'ri va xavfsiz standart hisoblanadi. "
                f"Bu kod tozaligi, ortiqcha SQL so'rovlarini oldini olish va tizim barqarorligini ta'minlaydi."
            )

        return JsonResponse({
            "success": True,
            "question_id": question.id,
            "question_text": question.text,
            "code_snippet": question.code_snippet,
            "question_type": question.question_type,
            "correct_choice": correct_text,
            "explanation": explanation_text,
            "category": question.category.name,
            "difficulty": question.get_difficulty_display(),
        })

