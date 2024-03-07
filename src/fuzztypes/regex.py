import re

from . import Entity, Match, MatchList, abstract, const


def Regex(
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
            # Create and append Entity for each match found
            entity = Entity(value=match)
            match_list.append(Match(key=match, entity=entity, is_alias=False))

        # Leave tiebreaker and error handling to MatchList.choose
        match_list.choose(min_score=0, tiebreaker_mode=tiebreaker_mode)

        return match_list

    return abstract.AbstractType(
        do_lookup,
        examples=examples,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )


Email = Regex(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    examples=["user@example.com"],
)

SSN = Regex(
    r"\b\d{3}-\d{2}-\d{4}\b",
    examples=["000-00-0000"],
)

ZipCode = Regex(
    r"\b\d{5}(?:-\d{4})?\b",
    examples=["12345", "12345-6789"],
)
