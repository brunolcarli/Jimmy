import graphene

import kinnon.schema


class Query(kinnon.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
