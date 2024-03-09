import os
from typing import Callable, Iterable, Union, List

from pydantic import PositiveInt

from fuzztypes import Match, MatchList, NamedEntity, abstract, const, flags
from .in_memory import Record

accelerators = {"cuda", "mps"}


class OnDiskStorage(abstract.AbstractStorage):
    def __init__(
        self,
        name: str,
        source: Iterable[NamedEntity],
        **kwargs,
    ):
        super().__init__(source, **kwargs)

        # todo: Hybrid search for OnDisk not yet implemented
        assert not self.search_flag.is_hybrid, "Hybrid search not supported"

        self.name = name
        self.db_path = os.path.join(const.FuzzOnDisk)
        self.conn = None
        self.table = None

    def prepare(self, force_drop_table: bool = False):
        try:
            # Note: lancedb is an Apache 2.0 licensed optional dependency.
            # You must import it yourself to use this functionality.
            # https://github.com/lancedb/lancedb
            import lancedb
            import pyarrow as pa

        except ImportError as err:
            raise RuntimeError("Import Failed: `pip install lancedb`") from err

        self.conn = lancedb.connect(self.db_path)

        if force_drop_table and self.name in set(self.conn.table_names()):
            self.conn.drop_table(self.name)

        if self.name not in set(self.conn.table_names()):
            self.create_table()

        self.table = self.conn.open_table(self.name)

    def create_table(self):
        import pyarrow as pa

        schema = pa.schema(
            [
                pa.field("term", pa.string()),
                pa.field("entity", pa.string()),
                pa.field("is_alias", pa.string()),
                pa.field(
                    "vector",
                    pa.list_(pa.float32(), self.vect_dimensions),
                ),
            ]
        )
        self.table = self.conn.create_table(
            self.name, schema=schema, exist_ok=True
        )

        # create records from source
        records = self.create_records()

        # calculate vectors in a batch
        if self.search_flag.is_semantic_ok:
            terms = [record.term for record in records]
            vectors = self.encode(terms)
            for record, vector in zip(records, vectors):
                record.vector = vector

        # add records in a batch to table
        self.table.add([record.model_dump() for record in records])

        # adjust num_partitions and num_sub_vectors based on dataset size
        num_records = len(records)

        if num_records > 256:  # pragma: no cover
            num_partitions = min(num_records, 256)
            num_sub_vectors = min(num_records, 96)
            index_cache_size = min(num_records, 256)
            accelerator = self.device if self.device in accelerators else None

            self.table.create_index(
                metric="cosine",
                num_partitions=num_partitions,
                num_sub_vectors=num_sub_vectors,
                vector_column_name="vector",
                replace=True,
                index_cache_size=index_cache_size,
                accelerator=accelerator,
            )

    def create_records(self):
        records = []
        empty = [0.0] * self.vect_dimensions
        for item in self.source:
            entity = NamedEntity.convert(item)
            json = entity.model_dump_json(exclude_defaults=True)

            terms = []
            is_alias = False

            if self.search_flag.is_name_ok:
                terms.append(entity.value)
                is_alias = True

            if self.search_flag.is_alias_ok:
                terms += entity.aliases

            for term in terms:
                # normalize for case sensitivity
                term = self.normalize(term)

                # construct and add record
                record = Record(
                    entity=json,
                    term=term,
                    is_alias=is_alias,
                    vector=empty,
                )
                records.append(record)

                # 2nd term and beyond are aliases
                is_alias = True

        return records

    #
    # Get Matches
    #

    def get(self, key: str) -> MatchList:
        where = f'term = "{self.normalize(key)}"'
        match_list = self.run_query(key, where=where)

        if not match_list:
            if self.search_flag.is_fuzz_ok:
                match_list = self.get_by_fuzz(key)

            if self.search_flag.is_semantic_ok:
                match_list = self.get_by_semantic(key)

        matches = MatchList(matches=match_list)
        return matches

    def get_by_fuzz(self, key: str) -> List[Match]:
        raise NotImplementedError

    def get_by_semantic(self, key: str) -> List[Match]:
        vector = self.encode([key])[0]
        return self.run_query(key, vector=vector)

    def run_query(self, key, where=None, vector=None) -> List[Match]:
        qb = self.table.search(query=vector, vector_column_name="vector")
        if vector is not None:
            qb = qb.metric("cosine")
        qb = qb.select(["entity", "term", "is_alias"])

        if where is not None:
            qb = qb.where(where, prefilter=True)

        qb = qb.limit(self.limit)
        data = qb.to_list()

        match_list = []
        for item in data:
            if vector is not None:
                distance = item.pop("_distance", 0.0)
                similarity = 1 - distance
                score = (similarity + 1) * 50
            else:
                score = 100.0  # Exact match
            record = Record.model_validate(item)
            match_list.append(record.to_match(key=key, score=score))

        return match_list


def OnDisk(
    identity: str,
    source: Iterable,
    *,
    case_sensitive: bool = False,
    device: str = None,
    examples: list = None,
    fuzz_scorer: const.FuzzScorer = "token_sort_ratio",
    limit: PositiveInt = 10,
    min_similarity: float = 80.0,
    notfound_mode: const.NotFoundMode = "raise",
    search_flag: flags.SearchFlag = flags.DefaultSearch,
    vect_encoder: Union[Callable, str, object] = None,
    tiebreaker_mode: const.TiebreakerMode = "raise",
    validator_mode: const.ValidatorMode = "before",
):
    storage = OnDiskStorage(
        identity,
        source,
        case_sensitive=case_sensitive,
        device=device,
        fuzz_scorer=fuzz_scorer,
        limit=limit,
        min_similarity=min_similarity,
        search_flag=search_flag,
        vect_encoder=vect_encoder,
        tiebreaker_mode=tiebreaker_mode,
    )

    return abstract.AbstractType(
        storage,
        EntityType=NamedEntity,
        examples=examples,
        input_type=str,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )
