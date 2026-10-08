from .models import UserScore


def record_user_score(user, category, score, total_questions, correct_answers=0, details=None):
    return UserScore.objects.create(
        user=user,
        category=category,
        score=score,
        total_questions=total_questions,
        correct_answers=correct_answers,
        details=details or [],
    )
