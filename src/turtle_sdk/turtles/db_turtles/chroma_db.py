import chromadb
import uuid

from bale_of_turtles import use_state, TurtleTool


class ChromaDbTurtle(TurtleTool):

    def add_document(self, **kwargs):
        raise NotImplementedError()

    def query_documents(self, **kwargs):
        raise NotImplementedError()


class ChromaDbTurtleMaker:

    def __init__(self, host: str, port: int, collection: str):
        super().__init__()
        self.client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=chromadb.Settings(allow_reset=True, anonymized_telemetry=False),
        )
        self.collection = collection

    def make_query_tool(
        self,
        search_query_key: str,
        return_query_key: str,
        save_statement_key: str,
        number_of_expected_results: int = 5,
    ) -> ChromaDbTurtle:
        search_fn_key = str(uuid.uuid5(uuid.NAMESPACE_DNS, search_query_key))
        save_fn_key = str(uuid.uuid5(uuid.NAMESPACE_DNS, save_statement_key))

        class QueryTurtleTool(ChromaDbTurtle):
            def __init__(
                self,
                client: chromadb.HttpClient,
                container: str,
            ):
                super(TurtleTool, self).__init__()
                self.collection = client.get_or_create_collection(container)

            @use_state(save_fn_key, update_on=[save_statement_key])
            def add_document(self, **kwargs):
                save_statement = kwargs.get(save_statement_key, None)
                if save_statement is None:
                    return
                if not isinstance(save_statement, str):
                    raise Exception("Cannot save non-string item in ChromaDb")
                self.collection.add(
                    documents=[save_statement],
                    ids=[str(uuid.uuid5(uuid.NAMESPACE_DNS, save_statement))],
                )

            @use_state(search_fn_key, update_on=[search_query_key])
            def query_documents(self, **kwargs):
                search_query = kwargs.get(search_query_key, None)
                if search_query is None:
                    return

                self.update_state(
                    **{
                        return_query_key: [
                            doc_str
                            for doc_strs in self.collection.query(
                                query_texts=[search_query_key],
                                n_results=number_of_expected_results,
                            )["documents"]
                            for doc_str in doc_strs
                        ]
                    }
                )

        return QueryTurtleTool(
            self.client,
            self.collection,
        )
