import json
from typing import ClassVar, List

import pyarrow as pa
from lancedb import LanceDBConnection
from lancedb.table import LanceTable

from fuzzterms import Database


class Table:
    name: ClassVar = None

    def __init__(self, db: Database, table: LanceTable):
        self.db = db
        self.table = table

    def add(self, data: List[dict]):
        self.table.add(data)

    def count(self) -> int:
        return self.table.count_rows()

    def update_indexes(self):
        pass

    @classmethod
    def columns(cls, db: Database) -> List[pa.Field]:
        raise NotImplementedError

    @classmethod
    def connect(cls, db: Database, conn: LanceDBConnection):
        if cls.name not in conn.table_names():
            table = cls.construct(db, conn)
        else:
            table = conn.open_table(cls.name)
        return cls(db=db, table=table)

    @classmethod
    def construct(cls, db: Database, conn: LanceDBConnection):
        schema = pa.schema(cls.columns(db))
        return conn.create_table(name=cls.name, schema=schema, exist_ok=True)


class TermsTable(Table):
    name: ClassVar = "terms"

    def update_indexes(self):
        self.table.create_fts_index(["term"], replace=True)

        num_records = self.table.count_rows()
        if num_records > 256:
            num_partitions = min(num_records, 256)
            num_sub_vectors = min(num_records, 96)
            index_cache_size = min(num_records, 256)
            accelerator = None
            if self.db.config.device in {"cuda", "mps"}:
                accelerator = self.db.config.device

            self.table.create_index(
                metric="cosine",
                num_partitions=num_partitions,
                num_sub_vectors=num_sub_vectors,
                vector_column_name="vector",
                replace=True,
                index_cache_size=index_cache_size,
                accelerator=accelerator,
            )

    @classmethod
    def columns(cls, db: Database) -> List[pa.Field]:
        columns = [
            pa.field("name", pa.string()),
            pa.field("label", pa.string()),
            pa.field("term", pa.string()),
            pa.field("is_alias", pa.bool_()),
            # pa.field("priority", pa.int64()),  # todo: add priority
        ]
        if db.config.vss_enabled:
            columns.append(
                pa.field(
                    "vector", pa.list_(pa.float32(), db.config.vss_dimensions)
                )
            )
        return columns


class EntitiesTable(Table):
    name: ClassVar = "entities"

    def add(self, data: List[dict]):
        entity_dicts = list(map(self._serialize_entity, data))
        super(EntitiesTable, self).add(entity_dicts)

    @classmethod
    def columns(cls, db: Database) -> List[pa.Field]:
        columns = [
            pa.field("name", pa.string()),
            pa.field("label", pa.string()),
            pa.field("priority", pa.int64()),
            pa.field("meta", pa.string()),
            # pa.field("aliases", pa.string()),  # todo: add to speed up.
        ]
        return columns

    # private methods

    @classmethod
    def _serialize_entity(cls, entity_dict: dict) -> dict:
        if "meta" in entity_dict and isinstance(entity_dict["meta"], dict):
            entity_dict = entity_dict.copy()
            # entity_dict["aliases"] = json.dumps(entity_dict["aliases"])
            entity_dict["meta"] = json.dumps(entity_dict["meta"])
        return entity_dict

    @classmethod
    def _deserialize_entity(cls, entity_dict: dict) -> dict:
        if "meta" in entity_dict and isinstance(entity_dict["meta"], str):
            entity_dict = entity_dict.copy()
            # entity_dict["aliases"] = json.loads(entity_dict["aliases"])
            entity_dict["meta"] = json.loads(entity_dict["meta"])
        return entity_dict
