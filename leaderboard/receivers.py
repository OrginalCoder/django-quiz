from django.dispatch import receiver
from quiz.signals import quiz_completed
from .services import record_user_score


@receiver(quiz_completed)
def handle_quiz_completed(sender, user, category, score, total_questions, correct_answers, details, **kwargs):
    return record_user_score(
        user=user,
        category=category,
        score=score,
        total_questions=total_questions,
        correct_answers=correct_answers,
        details=details,
    )
