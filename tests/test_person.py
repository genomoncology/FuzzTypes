from typing import Optional

from pydantic import BaseModel, ValidationError

from fuzztypes import Person, validate_python


class MyModel(BaseModel):
    person: Person
    optional: Optional[Person] = None


def test_example():
    person = validate_python(Person, "Mr. John (Johnny) Q. Public IV")
    assert str(person) == "Mr. John Q. Public IV (Johnny)"
    assert person.last_name_first == "Public, John Q."
    assert person.short_name == "John Public"
    assert person.legal_name == "John Q. Public IV"
    assert person.full_name == "Mr. John Q. Public IV (Johnny)"

    assert person.initials == "J. Q. P."
    assert person.full_initials == "J. Q. P."
    assert person.short_initials == "J. P."

    obj2 = MyModel(person=person)
    assert obj2.person == person
    assert obj2.person.human_name() == person.human_name()

    assert obj2.optional is None


def test_mixed_capitalization_with_validate_python():
    person = validate_python(Person, "shirley maclaine")
    assert person.first == "Shirley"
    assert person.last == "MacLaine"


def test_different_nickname_format_oh_well():
    obj = MyModel(person="Arthur 'The Fonz' Fonzerelli")
    assert obj.person.first == "Arthur"
    assert obj.person.last == "Fonzerelli"
    assert obj.person.middle == "'the Fonz'"
    assert str(obj.person) == "Arthur 'the Fonz' Fonzerelli"


def test_json_serialization():
    json = '{"person": "Grace Hopper"}'
    obj = MyModel.model_validate_json(json)
    assert str(obj.person) == "Grace Hopper"

    data = dict(person="grace hopper")
    obj = MyModel.model_validate(data)
    assert str(obj.person) == "Grace Hopper"

    json = obj.model_dump_json(exclude_defaults=True)
    assert json == '{"person":{"first":"Grace","last":"Hopper"}}'
    obj = MyModel.model_validate_json(json)

    data = obj.model_dump(exclude_defaults=True)
    assert data == dict(person=dict(first="Grace", last="Hopper"))


def test_value_error():
    try:
        assert MyModel(person=None).person is None
        assert False, "Didn't fail as expected."
    except ValidationError:
        pass

    try:
        assert MyModel(person=5)
        assert False, "Didn't fail as expected."
    except ValueError:
        pass
