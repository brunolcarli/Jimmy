from django.db import models


class Question(models.Model):
    question = models.CharField(max_length=500, null=False, blank=False, unique=True)
    scope = models.TextField()


class Answer(models.Model):
     user_id = models.CharField(max_length=255, null=True, blank=True)
     username = models.CharField(max_length=255, null=True, blank=True)
     is_anonymous = models.BooleanField(null=True)
     text_answer = models.TextField(null=False)
     question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
     datetime = models.DateTimeField(auto_now_add=True)
     sentiment = models.BooleanField(null=True)
