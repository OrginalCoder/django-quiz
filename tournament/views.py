import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from .models import Tournament, TournamentParticipation
from leaderboard.models import award_badges
from leaderboard.services import record_user_score


class TournamentListView(ListView):
    model = Tournament
    template_name = "tournament/tournament_list.html"
    context_object_name = "tournaments"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["active_tournaments"] = Tournament.objects.filter(is_active=True, start_date__lte=now, end_date__gte=now)
        context["past_tournaments"] = Tournament.objects.filter(end_date__lt=now) | Tournament.objects.filter(is_active=False)
        context["upcoming_tournaments"] = Tournament.objects.filter(is_active=True, start_date__gt=now)

        if self.request.user.is_authenticated:
            user_participations = {
                p.tournament_id: p for p in TournamentParticipation.objects.filter(user=self.request.user)
            }
            context["user_participations"] = user_participations
        return context


class TournamentDetailView(DetailView):
    model = Tournament
    template_name = "tournament/tournament_detail.html"
    context_object_name = "tournament"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        participation = None
        if user.is_authenticated:
            participation = TournamentParticipation.objects.filter(tournament=self.object, user=user).first()
        context["participation"] = participation
        context["top_participants"] = self.object.participations.select_related("user").order_by("-score", "time_spent_seconds")[:5]
        return context


class TournamentPlayView(LoginRequiredMixin, View):
    def get(self, request, pk):
        tournament = get_object_or_404(Tournament.objects.prefetch_related("questions", "questions__choices"), pk=pk)
        now = timezone.now()

        if tournament.is_upcoming:
            messages.warning(request, "Ushbu turnir hali boshlanmagan!")
            return redirect("tournament:detail", pk=tournament.pk)

        if tournament.is_ended:
            messages.warning(request, "Ushbu turnir yakunlangan!")
            return redirect("tournament:leaderboard", pk=tournament.pk)

        participation = TournamentParticipation.objects.filter(tournament=tournament, user=request.user).first()
        if participation and participation.completed_at:
            messages.info(request, "Siz ushbu turnirni allaqachon yakunlagansiz!")
            return redirect("tournament:leaderboard", pk=tournament.pk)

        if not participation:
            participation = TournamentParticipation.objects.create(
                tournament=tournament,
                user=request.user,
                total_questions=tournament.questions.count()
            )

        questions = list(tournament.questions.all().order_by("id"))
        questions_payload = []
        letters = ["A", "B", "C", "D", "E"]
        for q in questions:
            choices = list(q.choices.all())
            choices_payload = []
            for idx, c in enumerate(choices):
                choices_payload.append({
                    "id": c.id,
                    "text": c.text,
                    "badge": letters[idx] if idx < len(letters) else str(idx + 1)
                })
            questions_payload.append({
                "id": q.id,
                "text": q.text,
                "difficulty": q.difficulty,
                "difficulty_display": q.get_difficulty_display(),
                "points": q.points,
                "code_snippet": q.code_snippet,
                "question_type": q.question_type,
                "choices": choices_payload
            })

        return render(request, "tournament/tournament_play.html", {
            "tournament": tournament,
            "participation": participation,
            "questions_json": json.dumps(questions_payload),
            "duration_seconds": tournament.duration_minutes * 60,
        })


class TournamentSubmitApiView(LoginRequiredMixin, View):
    def post(self, request, pk):
        tournament = get_object_or_404(Tournament.objects.prefetch_related("questions", "questions__choices"), pk=pk)
        participation = get_object_or_404(TournamentParticipation, tournament=tournament, user=request.user)

        if participation.completed_at:
            return JsonResponse({"error": "Turnir allaqachon topshirilgan"}, status=400)

        try:
            body = json.loads(request.body)
            answers = body.get("answers", {})
            time_spent = int(body.get("time_spent_seconds", 0))
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({"error": "Noto'g'ri ma'lumot formati"}, status=400)

        questions = list(tournament.questions.all())
        total_score = 0
        correct_count = 0
        details = []

        for q in questions:
            user_choice_id = answers.get(str(q.id))
            correct_choice = next((c for c in q.choices.all() if c.is_correct), None)
            is_correct = False
            selected_choice = None
            if user_choice_id:
                selected_choice = next((c for c in q.choices.all() if c.id == int(user_choice_id)), None)
                if selected_choice and selected_choice.is_correct:
                    is_correct = True
                    correct_count += 1
                    total_score += q.points

            details.append({
                "question_text": q.text,
                "difficulty": q.difficulty,
                "difficulty_display": q.get_difficulty_display(),
                "points": q.points,
                "points_earned": q.points if is_correct else 0,
                "selected_choice_text": selected_choice.text if selected_choice else "Javob berilmadi",
                "correct_choice_text": correct_choice.text if correct_choice else "",
                "is_correct": is_correct,
            })

        participation.score = total_score
        participation.correct_answers = correct_count
        participation.total_questions = len(questions)
        participation.time_spent_seconds = time_spent
        participation.completed_at = timezone.now()
        participation.save()

        first_cat = questions[0].category if questions else None
        record_user_score(
            user=request.user,
            category=first_cat,
            score=total_score,
            total_questions=len(questions),
            correct_answers=correct_count,
            details=details,
        )

        award_badges(request.user)

        return JsonResponse({
            "success": True,
            "score": total_score,
            "correct_answers": correct_count,
            "redirect_url": reverse("tournament:leaderboard", kwargs={"pk": tournament.pk})
        })


class TournamentLeaderboardView(DetailView):
    model = Tournament
    template_name = "tournament/tournament_leaderboard.html"
    context_object_name = "tournament"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participants = self.object.participations.select_related("user").filter(completed_at__isnull=False).order_by("-score", "time_spent_seconds")
        context["participants"] = participants
        if self.request.user.is_authenticated:
            my_part = participants.filter(user=self.request.user).first()
            context["my_participation"] = my_part
            if my_part:
                p_list = list(participants)
                context["my_rank"] = p_list.index(my_part) + 1 if my_part in p_list else None
        return context
