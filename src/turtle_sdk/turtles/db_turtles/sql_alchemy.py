import uuid

from bale_of_turtles import use_state, TurtleTool
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Query

from turtle_sdk.turtles.turtle_tool_maker import make_fn_key


class SqlAlchemyTurtle(TurtleTool):

    def __init__(
        self,
        url: str,
        model: DeclarativeBase,
        search_query_key: str,
        return_query_key: str,
        save_statement_key: str,
        select_statement: Query,
    ):
        super().__init__()
        self.engine = create_engine(url)
        self.model = model
        self.save_statement_key = save_statement_key
        self.return_query_key = return_query_key
        self.select_statement = select_statement

        self.add_model = use_state(make_fn_key("add-model"), [save_statement_key])(
            self._add_model
        )
        self.search_model = use_state(make_fn_key("search-model"), [search_query_key])(
            self._search_model
        )

    def _add_model(self, **kwargs):
        save_model = kwargs.get(self.save_statement_key, None)
        if save_model is None:
            return

        if not isinstance(self.model, DeclarativeBase):
            raise Exception("Expected ORM got {}".format(type(self.model)))

        with Session(self.engine, commit=True) as session:
            session.add(save_model)

    def _search_model(self, **kwargs):
        save_model = kwargs.get(self.save_statement_key, None)
        if save_model is None:
            return

        self.update_state(**{self.return_query_key: list(self.select_statement)})
