from fuzzterms import Collection, Database, Encoder


class Searcher:
    def __init__(self, collection: Collection):
        self.collection = collection

    @property
    def database(self) -> Database:
        return self.collection.database

    @property
    def encoder(self) -> Encoder:
        return self.collection.encoder

    def hybrid_search(self, query, limit=10):
        vector = self.encoder.encode([query])[0]
        return self.database.hybrid_search(query, vector, limit)
