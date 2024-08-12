import uuid

from bale_of_turtles import use_state, TurtleTool
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Query

from turtle_sdk.turtles.turtle_tool_maker import TurtleToolMaker


class SqlAlchemyTurtle(TurtleTool):

    def add_model(self, **kwargs):
        raise NotImplementedError

    def search_model(self, **kwargs):
        raise NotImplementedError


class SqlAlchemyTurtleMaker(TurtleToolMaker):

    def __init__(self, url: str):
        self.engine = create_engine(url)

    def make_query_tool(
        self,
        model: DeclarativeBase,
        search_query_key: str,
        return_query_key: str,
        save_statement_key: str,
        select_statement: Query,
    ) -> SqlAlchemyTurtle:
        search_fn_key = str(uuid.uuid5(uuid.NAMESPACE_DNS, search_query_key))
        save_fn_key = str(uuid.uuid5(uuid.NAMESPACE_DNS, save_statement_key))

        with Session(self.engine):
            # noinspection PyUnresolvedReferences
            model.__table__.create(bind=self.engine, checkfirst=True)

        class QueryTurtleTool(SqlAlchemyTurtle):
            def __init__(self, engine, _model: DeclarativeBase):
                super().__init__()
                self.engine = engine
                self.model = model

            @use_state(save_fn_key, [save_statement_key])
            def add_model(self, **kwargs):
                save_model = kwargs.get(save_statement_key, None)
                if save_model is None:
                    return

                if not isinstance(model, DeclarativeBase):
                    raise Exception("Expected ORM got {}".format(type(model)))

                with Session(self.engine, commit=True) as session:
                    session.add(save_model)

            @use_state(search_fn_key, [search_query_key])
            def search_model(self, **kwargs):
                save_model = kwargs.get(save_statement_key, None)
                if save_model is None:
                    return

                self.update_state(**{return_query_key: list(select_statement)})

        return QueryTurtleTool(self.engine, model)
