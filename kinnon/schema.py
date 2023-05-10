import graphene
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

    questions = graphene.List(QuestionType)
    def resolve_questions(self, info, **kwargs):
        return Question.objects.filter(**kwargs)

    answers = graphene.List(AnswerType)
    def resolve_answers(self, info, **kwargs):
        return Answer.objects.filter(**kwargs)


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
