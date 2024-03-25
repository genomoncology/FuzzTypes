## v0.1.0 (2023-03-25)

The project's typing system was validated using mypy and refactored to follow
Annotated types as specified by [PEP 593](https://peps.python.org/pep-0593/).

#### Added
 - FuzzValidator annotation type created to simplify design
 - validate_python, validate_json, and validate_entity functions added
 - Added Language, LanguageName, and LanguageCode usable types
 - fuzztypes.logger and fuzztypes.utils module for downloading iso codes

#### Changed
 - Renamed OnDisk to OnDiskValidator
 - Renamed InMemory to MemoryValidator
 - Refactored InMemoryValidator and OnDiskValidator to use FuzzValidator
 - Refactored Person to use FuzzValidator
 - Renamed Regex to RegexValidator

#### Removed
 - abstract.py module and AbstractType class, simplified by FuzzValidator
 - function.py module and Function annotation type, replaced by FuzzValidator