import calendar
from datetime import datetime, timedelta
import pytz
import graphene
from django.db.models import Count
from django.conf import settings
from kinnon.models import Question, Answer
from kinnon.util import get_sentiment_week_progress



class UserStatistics(graphene.ObjectType):
    user_id = graphene.String()
    username = graphene.String()
    questions_answered = graphene.Int()
    questions_answered_today = graphene.Int()
    questions_answered_last_week = graphene.Int()
    questions_answered_last_month = graphene.Int()
    positive_sentiments = graphene.Int()
    negative_sentiments = graphene.Int()
    average_sentiment = graphene.Float()
    first_answer_datetime = graphene.DateTime()
    last_answer_datetime = graphene.DateTime()
    last_week_sentiment_progress = graphene.List(graphene.Float)


class QuestionType(graphene.ObjectType):
    id = graphene.ID()
    question = graphene.String()
    scope = graphene.String()
    answers = graphene.List('kinnon.schema.AnswerType')

    def resolve_answers(self, info, **kwargs):
        return self.answer_set.all()


class AnswerType(graphene.ObjectType):
    user_id = graphene.String()
    username = graphene.String()
    is_anonymous = graphene.Boolean()
    text_answer = graphene.String()
    question = graphene.Field(QuestionType)
    datetime = graphene.DateTime()
    sentiment = graphene.Boolean()

    def resolve_datetime(self, info, **kwargs):
        """
        Resolve datetime to GMT-3 (America/Sao_Paulo)
        """
        return self.datetime.astimezone(pytz.timezone('America/Sao_Paulo'))


class Query:
    version = graphene.String(description='Query API version')
    def resolve_version(self, info, **kwargs):
        return settings.VERSION

    questions = graphene.List(
        QuestionType,
        id=graphene.ID(),
        id__in=graphene.List(graphene.ID),
        question=graphene.String(),
        question__icontains=graphene.String(),
        scope=graphene.String(),
        scope__in=graphene.List(graphene.String)
    )
    def resolve_questions(self, info, **kwargs):
        return Question.objects.filter(**kwargs)

    answers = graphene.List(
        AnswerType,
        user_id=graphene.String(),
        user_id__in=graphene.List(graphene.String),
        username=graphene.String(),
        username__icontains=graphene.String(),
        username__in=graphene.List(graphene.String),
        is_anonymous=graphene.Boolean(),
        sentiment=graphene.Boolean(),
        question__id=graphene.ID(),
        text_answer__icontains=graphene.String(),
        datetime__gte=graphene.DateTime(),
        datetime__lte=graphene.DateTime()
    )
    def resolve_answers(self, info, **kwargs):
        return Answer.objects.filter(**kwargs)

    less_answered_question  = graphene.Field(QuestionType)

    def resolve_less_answered_question(self, info, **kwargs):
        return Question.objects.annotate(Count('answer')).order_by('answer').first()

    most_answered_question = graphene.Field(QuestionType)

    def resolve_most_answered_question(self, info, **kwargs):
        return Question.objects.annotate(Count('answer')).order_by('answer').last()

    last_answer = graphene.Field(
        AnswerType,
        user_id=graphene.String(required=True)
    )

    def resolve_last_answer(self, info, **kwargs):
        return Answer.objects.filter(user_id=kwargs['user_id']).last()

    user_statistics = graphene.Field(
        UserStatistics,
        user_id=graphene.String(required=True)
    )

    def resolve_user_statistics(self, info, **kwargs):
        answers = Answer.objects.filter(user_id=kwargs['user_id'])
        total = answers.count()
        positives = answers.filter(sentiment=True).count()
        negatives = answers.filter(sentiment=False).count()
        today = datetime.today()
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(
            days=max(calendar.monthcalendar(today.year, today.month)[-1])
        )

        return {
            'user_id': kwargs['user_id'],
            'username': answers.first().username,
            'questions_answered': total,
            'questions_answered_today': answers.filter(datetime=today).count(),
            'questions_answered_last_week': answers.filter(
                datetime__gte=last_week, datetime__lt=today).count(),
            'questions_answered_last_month': answers.filter(
                datetime__gte=last_month, datetime__lt=today).count(),
            'positive_sentiments': positives,
            'negative_sentiments': negatives,
            'average_sentiment': positives / total,
            'first_answer_datetime': answers.first().datetime.astimezone(pytz.timezone('America/Sao_Paulo')),
            'last_answer_datetime': answers.last().datetime.astimezone(pytz.timezone('America/Sao_Paulo')),
            'last_week_sentiment_progress': get_sentiment_week_progress(
                answers.filter(datetime__gte=last_week, datetime__lt=today)
            )
        }


class CreateAnswer(graphene.relay.ClientIDMutation):
    answer = graphene.Field(AnswerType)

    class Input:
        user_id = graphene.String()
        username = graphene.String()
        text_answer = graphene.String(required=True)
        question_id = graphene.ID(required=True)
        sentiment = graphene.Boolean()

    def mutate_and_get_payload(self, info, **kwargs):
        username = kwargs.get('username')
        user_id = kwargs.get('user_id')
        if (not username) and (not user_id):
            is_anonymous = True
        else:
            is_anonymous = False

        try:
            question = Question.objects.get(id=kwargs.get('question_id'))
        except Question.DoesNotExist:
            raise Exception('Invalid or not found question!')

        answer = Answer.objects.create(
            user_id=user_id,
            username=username,
            is_anonymous=is_anonymous,
            text_answer=kwargs['text_answer'],
            question=question,
            sentiment=kwargs.get('sentiment')
        )
        answer.save()

        return CreateAnswer(answer)


class Mutation:
    create_answer = CreateAnswer.Field()
