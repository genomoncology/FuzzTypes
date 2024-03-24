from typing import Annotated, Optional

from pydantic import BaseModel

from fuzztypes import FuzzValidator, lazy

FULL_NAME = "{title} {first} {middle} {last} {suffix} ({nickname})"
SHORT_NAME = "{first} {last}"
LEGAL_NAME = "{first} {middle} {last} {suffix}"
LAST_NAME_FIRST = "{last}, {first} {middle}"

FULL_INIT = "{first} {middle} {last}"
SHORT_INIT = "{first} {last}"


def parse(**kwargs):
    HumanName = lazy.lazy_import("nameparser", "HumanName")
    return HumanName(**kwargs)


class PersonModel(BaseModel):
    name_format: str = FULL_NAME
    init_format: str = FULL_INIT
    title: str = ""
    first: str = ""
    middle: str = ""
    last: str = ""
    suffix: str = ""
    nickname: str = ""

    def __str__(self):
        return self.name

    # names

    @property
    def name(self) -> str:
        return str(self.human_name())

    @property
    def full_name(self) -> str:
        return str(self.human_name(name_format=FULL_NAME))

    @property
    def short_name(self) -> str:
        return str(self.human_name(name_format=SHORT_NAME))

    @property
    def legal_name(self) -> str:
        return str(self.human_name(name_format=LEGAL_NAME))

    @property
    def last_name_first(self) -> str:
        return str(self.human_name(name_format=LAST_NAME_FIRST))

    # initials

    @property
    def initials(self) -> str:
        return self.human_name().initials()

    @property
    def full_initials(self) -> str:
        return self.human_name(init_format=FULL_INIT).initials()

    @property
    def short_initials(self) -> str:
        return self.human_name(init_format=SHORT_INIT).initials()

    # human name object from nameparser library

    def human_name(self, name_format=None, init_format=None):
        name_format = name_format or self.name_format
        init_format = init_format or self.init_format
        return parse(
            string_format=name_format,
            initials_format=init_format,
            title=self.title,
            first=self.first,
            middle=self.middle,
            last=self.last,
            suffix=self.suffix,
            nickname=self.nickname,
        )


def PersonValidator(
    name_format: str = FULL_NAME,
    init_format: str = FULL_INIT,
    capitalize: bool = True,
):
    def to_person(key) -> Optional[PersonModel]:
        if isinstance(key, str):
            human_name = parse(full_name=key)
            if capitalize:
                human_name.capitalize(force=True)
            data = human_name.as_dict()
            person = PersonModel(
                name_format=name_format, init_format=init_format, **data
            )
        elif isinstance(key, PersonModel):
            person = key
        elif isinstance(key, dict):
            person = PersonModel(**key)
        else:
            raise ValueError(f"Unexpected key type {type(key)} for {key}.")

        return person

    return FuzzValidator(to_person)


# default annotation
Person = Annotated[PersonModel, PersonValidator()]
