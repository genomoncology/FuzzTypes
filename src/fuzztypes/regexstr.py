import re

from . import FuzzType, Entity, Match, MatchList, const


def RegexStr(
    pattern: str,
    examples: list = None,
    notfound_mode: const.NotFoundMode = "raise",
    validator_mode: const.ValidatorMode = "before",
    tiebreaker_mode: const.TiebreakerMode = "raise",
):
    regex = re.compile(pattern)

    def do_lookup(key: str) -> MatchList:
        matches = regex.findall(key)
        match_list = MatchList()

        for match in matches:
            # Create and append NamedEntity for each match found
            entity = Entity(value=match)
            match_list.append(Match(key=match, entity=entity, is_alias=False))

        # Leave tiebreaker and error handling to MatchList.apply
        match_list.apply(min_score=0, tiebreaker_mode=tiebreaker_mode)

        return match_list

    return FuzzType(
        do_lookup,
        examples=examples,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )


Email = RegexStr(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    examples=["user@example.com"],
)

SSN = RegexStr(
    r"\b\d{3}-\d{2}-\d{4}\b",
    examples=["000-00-0000"],
)

ZipCode = RegexStr(
    r"\b\d{5}(?:-\d{4})?\b",
    examples=["12345", "12345-6789"],
)
