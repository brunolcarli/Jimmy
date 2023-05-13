import graphene
from django.db.models import Count
from kinnon.models import Question, Answer
from django.conf import settings


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
        return Question.objects.order_by().annotate(Count('answer')).last()


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
