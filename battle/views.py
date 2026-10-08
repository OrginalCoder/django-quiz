import json
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .models import BattleRoom
from quiz.models import Category, Question, Choice


class BattleLobbyView(LoginRequiredMixin, TemplateView):
    template_name = "battle/lobby.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["categories"] = Category.objects.all()
        context["waiting_rooms"] = BattleRoom.objects.filter(status="waiting").exclude(creator=user).select_related("creator", "category")[:10]
        context["my_waiting_rooms"] = BattleRoom.objects.filter(status="waiting", creator=user).select_related("category")
        context["recent_battles"] = BattleRoom.objects.filter(status="finished").filter(
            creator=user
        ).select_related("creator", "opponent", "winner") | BattleRoom.objects.filter(status="finished", opponent=user).select_related("creator", "opponent", "winner")
        context["recent_battles"] = context["recent_battles"].order_by("-created_at")[:6]

        total_battles = BattleRoom.objects.filter(status="finished").filter(creator=user).count() + BattleRoom.objects.filter(status="finished", opponent=user).count()
        wins = BattleRoom.objects.filter(status="finished", winner=user).count()
        context["total_battles"] = total_battles
        context["wins"] = wins
        return context


class BattleCreateView(LoginRequiredMixin, View):
    def post(self, request):
        category_slug = request.POST.get("category_slug")
        category = Category.objects.filter(slug=category_slug).first() if category_slug else None

        room_code = f"BTL-{uuid.uuid4().hex[:6].upper()}"

        questions_qs = Question.objects.all()
        if category:
            questions_qs = questions_qs.filter(category=category)

        questions = list(questions_qs.order_by("?")[:5])
        if len(questions) < 5:
            questions = list(Question.objects.order_by("?")[:5])

        if len(questions) < 3:
            messages.error(request, "Bellashuv uchun yetarli savollar topilmadi.")
            return redirect("battle:lobby")

        room = BattleRoom.objects.create(
            room_code=room_code,
            category=category,
            creator=request.user,
            status="waiting"
        )
        room.questions.set(questions)

        return redirect("battle:room", room_code=room.room_code)


class BattleRoomView(LoginRequiredMixin, DetailView):
    model = BattleRoom
    slug_field = "room_code"
    slug_url_kwarg = "room_code"
    template_name = "battle/room.html"
    context_object_name = "room"

    def get_object(self, queryset=None):
        room = super().get_object(queryset)
        user = self.request.user
        if room.status == "waiting" and room.creator != user and room.opponent is None:
            room.opponent = user
            room.status = "active"
            room.save()
        return room

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.object
        context["is_creator"] = (self.request.user == room.creator)
        context["is_participant"] = (self.request.user in [room.creator, room.opponent])
        return context


class BattleStateApiView(LoginRequiredMixin, View):
    def get(self, request, room_code):
        room = get_object_or_404(BattleRoom.objects.prefetch_related("questions", "questions__choices"), room_code=room_code)
        user = request.user

        is_creator = (user == room.creator)
        is_opponent = (user == room.opponent)

        if not (is_creator or is_opponent):
            return JsonResponse({"error": "Siz ushbu xona qatnashchisi emassiz"}, status=403)

        questions_list = list(room.questions.all().order_by("id"))
        total_q = len(questions_list)

        user_progress = room.creator_progress if is_creator else room.opponent_progress
        user_score = room.creator_score if is_creator else room.opponent_score
        enemy_username = room.opponent.username if is_creator and room.opponent else (room.creator.username if is_opponent else "Kutilmoqda...")
        enemy_progress = room.opponent_progress if is_creator else room.creator_progress
        enemy_score = room.opponent_score if is_creator else room.creator_score

        current_question_data = None
        if room.status == "active" and user_progress < total_q:
            q = questions_list[user_progress]
            choices = list(q.choices.all())
            letters = ["A", "B", "C", "D", "E"]
            choices_data = []
            for idx, c in enumerate(choices):
                choices_data.append({
                    "id": c.id,
                    "text": c.text,
                    "badge": letters[idx] if idx < len(letters) else str(idx + 1)
                })

            current_question_data = {
                "id": q.id,
                "text": q.text,
                "difficulty_display": q.get_difficulty_display(),
                "points": q.points,
                "choices": choices_data,
            }

        winner_name = None
        if room.status == "finished":
            if room.winner:
                winner_name = room.winner.username
            else:
                winner_name = "Durang"

        return JsonResponse({
            "status": room.status,
            "my_username": user.username,
            "my_score": user_score,
            "my_progress": user_progress,
            "enemy_username": enemy_username,
            "enemy_score": enemy_score,
            "enemy_progress": enemy_progress,
            "total_questions": total_q,
            "current_question": current_question_data,
            "winner": winner_name,
        })


class BattleAnswerApiView(LoginRequiredMixin, View):
    def post(self, request, room_code):
        room = get_object_or_404(BattleRoom.objects.prefetch_related("questions", "questions__choices"), room_code=room_code)
        user = request.user

        is_creator = (user == room.creator)
        is_opponent = (user == room.opponent)

        if not (is_creator or is_opponent):
            return JsonResponse({"error": "Ruxsat etilmagan"}, status=403)

        if room.status != "active":
            return JsonResponse({"error": "Bellashuv faol emas"}, status=400)

        try:
            body = json.loads(request.body)
            question_id = int(body.get("question_id"))
            choice_id = int(body.get("choice_id")) if body.get("choice_id") is not None else None
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({"error": "Noto'g'ri format"}, status=400)

        questions_list = list(room.questions.all().order_by("id"))
        user_progress = room.creator_progress if is_creator else room.opponent_progress

        if user_progress >= len(questions_list) or questions_list[user_progress].id != question_id:
            return JsonResponse({"error": "Noto'g'ri savol ketma-ketligi"}, status=400)

        question = questions_list[user_progress]
        choices = list(question.choices.all())
        correct_choice = next((c for c in choices if c.is_correct), None)
        selected_choice = next((c for c in choices if c.id == choice_id), None) if choice_id else None

        is_correct = bool(selected_choice and selected_choice.is_correct)
        points_earned = question.points if is_correct else 0

        if is_creator:
            room.creator_score += points_earned
            room.creator_progress += 1
        else:
            room.opponent_score += points_earned
            room.opponent_progress += 1

        total_q = len(questions_list)
        if room.creator_progress >= total_q and room.opponent_progress >= total_q:
            room.status = "finished"
            if room.creator_score > room.opponent_score:
                room.winner = room.creator
            elif room.opponent_score > room.creator_score:
                room.winner = room.opponent
            else:
                room.winner = None
            if room.winner:
                from leaderboard.models import award_badges
                award_badges(room.winner)

        room.save()

        return JsonResponse({
            "is_correct": is_correct,
            "correct_choice_id": correct_choice.id if correct_choice else None,
            "points_earned": points_earned,
            "room_status": room.status,
        })
