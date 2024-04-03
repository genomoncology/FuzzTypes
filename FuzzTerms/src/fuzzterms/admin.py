from typing import Iterable

from fuzzterms import Collection, Config, Database, Encoder, Entity, Stats


class Admin:
    def __init__(self, collection: Collection):
        self.collection: Collection = collection
        self.config: Config = collection.config

    @property
    def database(self) -> Database:
        return self.collection.database

    @property
    def encoder(self) -> Encoder:
        return self.collection.encoder

    def stats(self):
        result = self.database.stats()
        return Stats(**result)

    def upsert(self, entities: Iterable[Entity]):
        batch_size = self.config.db_batch_size
        while True:
            i = 0
            entities = []
            terms = []

            for entity in entities:
                record = entity.model_dump()
                entities.append(record)
                terms.append(entity.name)
                terms += entity.aliases or []

                i += 1
                if i > batch_size:
                    break

            vectors = self.encoder(terms)

        # todo: implement database.upsert for entities and terms with vectors
