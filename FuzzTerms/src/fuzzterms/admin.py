from typing import Iterable, List, Tuple, Union

from pydantic import TypeAdapter

from fuzzterms import Collection, Config, Database, Encoder, Entity, Stats


class Batch:
    def __init__(self, batch_size, encoder):
        self.batch_size = batch_size
        self.encoder = encoder
        self.rows = []
        self.total_count = 0
        self.adapter = TypeAdapter(List[Entity])

    def is_full(self):
        return len(self.rows) >= self.batch_size

    def add(self, row: dict):
        self.rows.append(row)
        self.total_count += 1

    def complete(self) -> Tuple[List[dict], List[dict]]:
        final_entities: List[dict] = []
        all_terms = []
        pks = []
        is_aliases = []

        def collect(entity: Entity):
            nonlocal final_entities, all_terms, pks, is_aliases
            as_dict: dict = entity.model_dump()
            final_entities.append(as_dict)
            this_terms = [entity.name] + entity.aliases
            all_terms += this_terms
            pks += [entity.pk] * len(this_terms)
            is_aliases += [False] + ([True] * (len(this_terms) - 1))

        # convert and collect all
        list(map(collect, self.adapter.validate_python(self.rows)))

        vectors = self.encoder(all_terms)
        zipped = zip(pks, all_terms, vectors, is_aliases)

        final_terms = []
        for (name, label), term, vector, is_alias in zipped:
            final_terms.append(
                {
                    "name": name,
                    "label": label,
                    "term": term,
                    "vector": vector,
                    "is_alias": is_alias,
                }
            )

        self.rows = []
        return final_entities, final_terms


class Admin:
    def __init__(self, collection: Collection, batch_size: int = None):
        self.collection: Collection = collection
        self.config: Config = collection.config
        self.batch_size = batch_size or self.config.batch_size

    @property
    def database(self) -> Database:
        return self.collection.database

    @property
    def encoder(self) -> Encoder:
        return self.collection.encoder

    def initialize(self):
        self.database.initialize()

    def stats(self):
        result = self.database.stats()
        return Stats(**result)

    def upsert(self, rows: Iterable[dict]) -> int:
        batch = Batch(self.batch_size, self.encoder)

        for row in rows:
            batch.add(row)
            if batch.is_full():
                entity_dicts, term_dicts = batch.complete()
                self.database.upsert(entity_dicts, term_dicts)

        entity_dicts, term_dicts = batch.complete()
        if entity_dicts or term_dicts:
            self.database.upsert(entity_dicts, term_dicts)

        return batch.total_count
