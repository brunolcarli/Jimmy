import graphene
from kinnon.models import Question, Answer
from django.conf import settings


class QuestionType(graphene.ObjectType):
    question = graphene.String()
    scope = graphene.String()


class AnswerType(graphene.ObjectType):
    user_id = graphene.String()
    username = graphene.String()
    is_anonymous = graphene.Boolean()
    text_answer = graphene.String()
    question = graphene.Field(QuestionType)
    datetime = graphene.DateTime()
    sentiment = graphene.Boolean()


class Query:
    version = graphene.String(description='Query API version')
    def resolve_version(self, info, **kwargs):
        return settings.VERSION

    questions = graphene.List(QuestionType)
    def resolve_questions(self, info, **kwargs):
        return Question.objects.filter(**kwargs)

    answers = graphene.List(AnswerType)
    def resolve_answers(self, info, **kwargs):
        return Answer.objects.filter(**kwargs)
