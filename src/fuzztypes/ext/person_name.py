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
        name = HumanName(key)

        if capitalize:
            name.capitalize(force=True)

        # Temporarily set string_format for this instance
        # {title} {first} {middle} {last} {suffix} ({nickname})
        if format_str is not None:
            name.string_format = format_str

        match_list = MatchList()
        formatted_name = str(name)
        if formatted_name:
            entity = NamedEntity(name=formatted_name)
            match_list.set(key=key, entity=entity)

        return match_list

    return FuzzType(
        do_lookup,
        examples=examples,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )


# Common patterns
AllName = PersonName("{title} {first} {middle} {last} {suffix} ({nickname})")
Bibliography = PersonName("{last}, {first} {middle}")
BusinessFormat = PersonName("{title} {first} {last}")
FirstLastName = PersonName("{first} {last}")
FirstNickLastName = PersonName("{first} {nickname} {last}")
FullName = PersonName("{title} {first} {middle} {last} {suffix}")
LegalName = PersonName("{first} {middle} {last} {suffix}")
NicknameOnly = PersonName("{nickname} {last}")
ProfessionalName = PersonName("{first} {middle} {last} {suffix}")
ProfessionalTitle = PersonName("{title} {last}")
