from enum import Flag, auto
from typing import Dict


class SearchFlag(Flag):
    NAME_OK = auto()
    ALIAS_OK = auto()
    FUZZ_OK = auto()
    SEMANTIC_OK = auto()

    @property
    def is_name_ok(self) -> bool:
        return bool(self & SearchFlag.NAME_OK)

    @property
    def is_alias_ok(self) -> bool:
        return bool(self & SearchFlag.ALIAS_OK)

    @property
    def is_fuzz_ok(self) -> bool:
        return bool(self & SearchFlag.FUZZ_OK)

    @property
    def is_semantic_ok(self) -> bool:
        return bool(self & SearchFlag.SEMANTIC_OK)

    @property
    def is_fuzz_or_semantic_ok(self):
        return self.is_fuzz_ok or self.is_semantic_ok

    @property
    def is_hybrid(self):
        return self.is_fuzz_ok and self.is_semantic_ok


NameSearch = SearchFlag.NAME_OK
AliasSearch = NameSearch | SearchFlag.ALIAS_OK
FuzzSearch = AliasSearch | SearchFlag.FUZZ_OK
SemanticSearch = AliasSearch | SearchFlag.SEMANTIC_OK
HybridSearch = FuzzSearch | SemanticSearch
DefaultSearch = AliasSearch

SearchMappings: Dict[str, SearchFlag] = {
    "name": NameSearch,
    "alias": AliasSearch,
    "fuzz": FuzzSearch,
    "semantic": SemanticSearch,
    "hybrid": HybridSearch,
    "default": DefaultSearch,
}
