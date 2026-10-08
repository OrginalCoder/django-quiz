from django.urls import path
from .views import (
    CategoryListView,
    CategoryDetailView,
    QuizView,
    QuizQuestionApiView,
    QuizAnswerApiView,
    MistakesListView,
    MistakesPracticeView,
    DailyChallengeView,
    DailyChallengeAnswerApiView,
    AiExplainApiView,
)

app_name = "quiz"

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("category/<slug:slug>/", CategoryDetailView.as_view(), name="category_detail"),
    path("mistakes/", MistakesListView.as_view(), name="mistakes_list"),
    path("mistakes/practice/", MistakesPracticeView.as_view(), name="mistakes_practice"),
    path("daily/", DailyChallengeView.as_view(), name="daily_challenge"),
    path("daily/answer/", DailyChallengeAnswerApiView.as_view(), name="daily_answer"),
    path("api/ai-explain/<int:question_id>/", AiExplainApiView.as_view(), name="ai_explain"),
    path("quiz/<slug:category_slug>/", QuizView.as_view(), name="quiz_screen"),
    path("quiz/<slug:category_slug>/question/", QuizQuestionApiView.as_view(), name="api_question"),
    path("quiz/<slug:category_slug>/answer/", QuizAnswerApiView.as_view(), name="api_answer"),
]
