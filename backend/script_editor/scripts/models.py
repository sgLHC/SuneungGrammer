# scripts/models.py

from django.db import models
from django.contrib.auth.models import User


class Script(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # 사용자와의 foreign 키 관계 설정
    original_text = models.TextField()  # 사용자가 제출한 원본 대본
    edited_text = models.TextField(blank=True, null=True)  # GPT가 수정한 대본
    audience_level = models.CharField(max_length=50, default="general")  # 청중 수준
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시간

    def __str__(self):
        return f"Script by {self.user.username} at {self.created_at}"


class GrammarRule(models.Model):
    # 문법 규칙 모델
    tag = models.CharField(
        max_length=100, unique=True
    )  # 문법 규칙의 태그 (예: SV_AGREEMENT)
    description = models.TextField()  # 문법 규칙에 대한 설명

    def __str__(self):
        return self.tag


class ExampleSentence(models.Model):
    # 예문 모델
    rule = models.ForeignKey(
        GrammarRule, on_delete=models.CASCADE, related_name="examples"
    )  # 해당 예문이 속하는 문법 규칙
    incorrect_sentence = models.TextField()  # 오류가 있는 예문
    corrected_sentence = models.TextField()  # 수정된 예문

    def __str__(self):
        return f"Example for {self.rule.tag}: {self.incorrect_sentence[:30]}..."

class QuestionMeta(models.Model):
    # 수능 영어 문제 메타데이터
    id = models.IntegerField(primary_key=True)
    question_type = models.CharField(max_length=100)  # 문제 유형
    question = models.TextField()              # 문제 본문
    options = models.TextField()                   # 보기 (콤마로 구분된 텍스트)
    vocabulary = models.CharField(max_length=100)   # 어휘
    answer = models.CharField(max_length=10)        # 정답
    explanation = models.TextField()                # 해설

    def __str__(self):
        return f"{self.problem_type}: {self.question_text[:50]}"
