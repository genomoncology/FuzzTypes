from typing import Iterable, List, Tuple

from fuzzterms import Collection, Config, Database, Encoder, Entity, Stats


class Batch:
    def __init__(self, batch_size, encoder):
        self.batch_size = batch_size
        self.encoder = encoder
        self.entities = []
        self.terms = []
        self.pks = []
        self.is_aliases = []
        self.total_count = 0

    def is_full(self):
        return len(self.entities) >= self.batch_size

    def reset(self):
        self.entities = []
        self.terms = []
        self.pks = []
        self.is_aliases = []

    def add(self, entity: Entity):
        self.total_count += 1

        # add to entities
        self.entities.append(entity.model_dump())
        # add to terms
        terms = [entity.name] + entity.aliases
        self.terms += terms
        self.pks += [entity.pk] * len(terms)
        self.is_aliases += ([False] + ([True] * (len(terms) - 1)))

    def complete(self) -> Tuple[List[dict], List[dict]]:
        vectors = self.encoder(self.terms)
        terms = []
        zipped = zip(self.pks, self.terms, vectors, self.is_aliases)
        for (name, label), term, vector, is_alias in zipped:
            terms.append({
                "name": name,
                "label": label,
                "term": term,
                "vector": vector,
                "is_alias": is_alias,
            })
        entities = self.entities[:]
        self.reset()

        return entities, terms


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

    def initialize(self):
        self.database.initialize()

    def stats(self):
        result = self.database.stats()
        return Stats(**result)

    def upsert(self, entities: Iterable[Entity]) -> int:
        batch = Batch(self.config.batch_size, self.encoder)

        for entity in entities:
            batch.add(entity)
            if batch.is_full():
                entity_dicts, term_dicts = batch.complete()
                self.database.upsert(entity_dicts, term_dicts)

        entity_dicts, term_dicts = batch.complete()
        if entity_dicts or term_dicts:
            self.database.upsert(entity_dicts, term_dicts)
