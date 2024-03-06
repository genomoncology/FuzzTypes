from enum import Flag, auto


# What NamedEntity fields does the search key need to match on?
# Does search support fuzzy matching and semantic similarity?
class SearchType(Flag):
    NAME_OK = auto()
    ALIAS_OK = auto()
    FUZZ_OK = auto()
    SEMANTIC_OK = auto()

    @property
    def is_name_ok(self) -> bool:
        return bool(self & SearchType.NAME_OK)

    @property
    def is_alias_ok(self) -> bool:
        return bool(self & SearchType.ALIAS_OK)

    @property
    def is_fuzz_ok(self) -> bool:
        return bool(self & SearchType.FUZZ_OK)

    @property
    def is_semantic_ok(self) -> bool:
        return bool(self & SearchType.SEMANTIC_OK)

    @property
    def is_fuzz_or_semantic_ok(self):
        return self.is_fuzz_ok or self.is_semantic_ok


NameSearch = SearchType.NAME_OK
AliasSearch = NameSearch | SearchType.ALIAS_OK
FuzzSearch = AliasSearch | SearchType.FUZZ_OK
SemanticSearch = AliasSearch | SearchType.SEMANTIC_OK
HybridSearch = FuzzSearch | SemanticSearch
DefaultSearch = AliasSearch
