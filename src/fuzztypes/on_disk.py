from typing import Callable, Iterable, Union, List, Type, Optional, Any

from pydantic import PositiveInt

from fuzztypes import (
    Match,
    MatchResult,
    NamedEntity,
    Record,
    abstract,
    const,
    flags,
    lazy,
    storage,
)

accelerators = {"cuda", "mps"}


class OnDiskStorage(storage.AbstractStorage):
    def __init__(
        self,
        name: str,
        source: Iterable[NamedEntity],
        **kwargs,
    ):
        super().__init__(source, **kwargs)

        self.name = name
        self._conn = None
        self._table = None

    @property
    def conn(self) -> Any:
        if self._conn is None:
            lancedb = lazy.lazy_import("lancedb")
            self._conn = lancedb.connect(const.OnDiskPath)
        return self._conn

    @property
    def table(self) -> Any:
        if self._table is None:
            self._table = self.conn.open_table(self.name)
        return self._table

    def prepare(self, force_drop_table: bool = False):
        table_names = set(self.conn.table_names(limit=999_999_999))

        if force_drop_table and self.name in table_names:
            self.conn.drop_table(self.name)
            table_names -= {self.name}

        if self.name not in table_names:
            try:
                self.create_table()
            except Exception as e:  # pragma: no cover
                # if any issue occurs, drop the table and re-raise error
                # in the future, handle errors better
                self.conn.drop_table(self.name)
                raise e

    def create_table(self):
        pa = lazy.lazy_import("pyarrow")

        schema = pa.schema(
            [
                pa.field("term", pa.string()),
                pa.field("norm_term", pa.string()),
                pa.field("entity", pa.string()),
                pa.field("is_alias", pa.string()),
                pa.field(
                    "vector",
                    pa.list_(pa.float32(), self.vect_dimensions),
                ),
            ]
        )
        table = self.conn.create_table(self.name, schema=schema, exist_ok=True)

        # create records from source
        records = self.create_records()

        # calculate vectors in a batch
        if self.search_flag.is_semantic_ok:
            terms = [record.term for record in records]
            vectors = self.encode(terms)
            for record, vector in zip(records, vectors):
                record.vector = vector

        # add records in a batch to table
        table.add([record.model_dump() for record in records])

        # adjust num_partitions and num_sub_vectors based on dataset size
        num_records = len(records)

        should_index = num_records > 256 and self.search_flag.is_semantic_ok

        if self.search_flag.is_fuzz_ok:  # pragma: no cover
            table.create_fts_index("term")

        if should_index:  # pragma: no cover
            num_partitions = min(num_records, 256)
            num_sub_vectors = min(num_records, 96)
            index_cache_size = min(num_records, 256)
            accelerator = self.device if self.device in accelerators else None

            table.create_index(
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
            entity = self.entity_type.convert(item)
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
                norm_term = self.normalize(term)

                # construct and add record
                if term:
                    record = Record(
                        entity=json,
                        term=term,
                        norm_term=norm_term,
                        is_alias=is_alias,
                        vector=empty,
                    )
                    records.append(record)

                # 2nd term and beyond are aliases
                is_alias = True

        return records

    #
    # Getters
    #

    def get(self, key: str) -> MatchResult:
        where = f'term = "{key}"'
        match_list = self.run_query(key, where=where)

        if not match_list:
            where = f'norm_term = "{self.normalize(key)}"'
            match_list = self.run_query(key, where=where)

        if not match_list:
            if self.search_flag.is_fuzz_ok:
                match_list = self.get_by_fuzz(key)

            if self.search_flag.is_semantic_ok:
                match_list = self.get_by_semantic(key)

        matches = MatchResult(matches=match_list)
        return matches

    def get_by_fuzz(self, key: str) -> List[Match]:
        query = self.normalize(key)
        match_list = self.run_query(key, vector=query)

        # re-scoring using rapidfuzz on matches
        terms = [match.term for match in match_list]
        extract = self.rapidfuzz.process.extract(
            query, terms, scorer=self.fuzz_scorer
        )
        for key, score, index in extract:
            match_list[index].score = score

        return match_list

    def get_by_semantic(self, key: str) -> List[Match]:
        vector = self.encode([key])[0]
        return self.run_query(key, vector=vector)

    def run_query(self, key, where=None, vector=None) -> List[Match]:
        qb = self.table.search(query=vector, vector_column_name="vector")

        if vector is not None and self.search_flag.is_semantic_ok:
            qb = qb.metric("cosine")

        qb = qb.select(["entity", "term", "norm_term", "is_alias"])

        if where is not None:
            qb = qb.where(where, prefilter=True)

        qb = qb.limit(self.limit)
        data = qb.to_list()

        match_list = []
        for item in data:
            if "_distance" in item:
                distance = item.pop("_distance", 0.0)
                similarity = 1 - distance
                score = (similarity + 1) * 50
            elif "score" in item:
                score = item.pop("score", 0.0)
            else:
                score = 100.0  # Exact match

            record = Record.model_validate(item)
            match = record.to_match(
                key=key, score=score, entity_type=self.entity_type
            )
            match_list.append(match)

        return match_list


def OnDisk(
    identity: str,
    source: Iterable[NamedEntity],
    *,
    case_sensitive: bool = False,
    device: Optional[const.DeviceList] = None,
    encoder: Union[Callable, str, object] = None,
    entity_type: Type[NamedEntity] = NamedEntity,
    examples: Optional[list] = None,
    fuzz_scorer: const.FuzzScorer = "token_sort_ratio",
    input_type=str,
    limit: PositiveInt = 10,
    min_similarity: float = 80.0,
    notfound_mode: const.NotFoundMode = "raise",
    search_flag: flags.SearchFlag = flags.DefaultSearch,
    tiebreaker_mode: const.TiebreakerMode = "raise",
    validator_mode: const.ValidatorMode = "before",
):
    source = OnDiskStorage(
        identity,
        source,
        case_sensitive=case_sensitive,
        device=device,
        entity_type=entity_type,
        fuzz_scorer=fuzz_scorer,
        limit=limit,
        min_similarity=min_similarity,
        search_flag=search_flag,
        encoder=encoder,
        tiebreaker_mode=tiebreaker_mode,
    )

    return abstract.AbstractType(
        source,
        EntityType=entity_type,
        examples=examples,
        input_type=input_type,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )
