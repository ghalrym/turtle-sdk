import uuid

import chromadb
from bale_of_turtles import use_state, TurtleTool

from turtle_sdk.turtles.turtle_tool_maker import make_fn_key


class ChromaDbTurtle(TurtleTool):
    __slots__ = (
        "client"
        "collection"
        "save_statement_key"
        "search_query_key"
        "search_query_key"
        "number_of_expected_results"
        "return_query_key"
        "add_document"
        "query_documents"
    )

    def __init__(
        self,
        host: str,
        port: int,
        collection: str,
        save_statement_key: str,
        search_query_key: str,
        return_query_key: str,
        number_of_expected_results: int = 5,
    ):
        TurtleTool.__init__(self)
        # Chroma DB Variables
        self.client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=chromadb.Settings(allow_reset=True, anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(collection)

        # State Variables
        self.save_statement_key = save_statement_key
        self.search_query_key = search_query_key
        self.search_query_key = search_query_key
        self.number_of_expected_results = number_of_expected_results
        self.return_query_key = return_query_key

        # Wrapped Methods
        self.add_document = use_state(
            make_fn_key("chroma-add-document"), update_on=[self.save_statement_key]
        )(self._add_document)
        self.query_documents = use_state(
            make_fn_key("chroma-query-document"), update_on=[search_query_key]
        )(self._query_documents)

    def _add_document(self, **kwargs):
        save_statement = kwargs.get(self.save_statement_key, None)
        if save_statement is None:
            return
        if not isinstance(save_statement, str):
            raise Exception("Cannot save non-string item in ChromaDb")
        self.collection.add(
            documents=[save_statement],
            ids=[str(uuid.uuid5(uuid.NAMESPACE_DNS, save_statement))],
        )

    def _query_documents(self, **kwargs):
        search_query = kwargs.get(self.search_query_key, None)
        if search_query is None:
            return

        db_results = [
            doc_str
            for doc_strs in self.collection.query(
                query_texts=[self.search_query_key],
                n_results=self.number_of_expected_results,
            )["documents"]
            for doc_str in doc_strs
        ]
        self.update_state(**{self.return_query_key: db_results})
