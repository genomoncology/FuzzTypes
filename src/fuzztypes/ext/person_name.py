from nameparser import HumanName

from fuzztypes import FuzzType, NamedEntity, MatchList, const


def PersonName(
    format_str: str = None,
    capitalize: bool = True,
    examples: list = None,
    notfound_mode: const.NotFoundMode = "raise",
    validator_mode: const.ValidatorMode = "before",
):
    def do_lookup(key: str) -> MatchList:
        value = HumanName(key)

        if capitalize:
            value.capitalize(force=True)

        # Temporarily set string_format for this instance
        # {title} {first} {middle} {last} {suffix} ({nickname})
        if format_str is not None:
            value.string_format = format_str

        match_list = MatchList()
        formatted_name = str(value)
        if formatted_name:
            entity = NamedEntity(value=formatted_name)
            match_list.set(key=key, entity=entity)

        return match_list

    return FuzzType(
        do_lookup,
        examples=examples,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )


FullName = PersonName("{title} {first} {middle} {last} {suffix} ({nickname})")
FirstLastName = PersonName("{first} {last}")
BibliographyName = PersonName("{last}, {first} {middle}")
LegalName = PersonName("{first} {middle} {last} {suffix}")
ProfessionalName = PersonName("{first} {middle} {last} {suffix}")
FirstNickLastName = PersonName("{first} '{nickname}' {last}")
