# LLM Direction

Dear coding assistant, thank you for your help with this project. This document has
some information that will be useful in helping me write code.

### Top Level Coding Goals

- Our top priority is creating simple python library with a coding interface that is simple and easy to understand.
- Code should be highly performance and easy to maintain. 
- Any backend that supports vector and full-text search should work. We are starting with SQLite and PostgreSQL.


### Pydantic 2 only

- Never recommend Pydantic 1 code.
- Namespace Updates: Method and attribute names now prefixed with `model_` or follow the `__.*pydantic.*__` pattern.
- Removal of GenericModel: Directly use `Generic` alongside `BaseModel` for generic model definitions.
- Deprecated Validators: Use `@field_validator` and `@model_validator` instead of `@validator` and `@root_validator`.
- Field Changes: `Field` no longer accepts arbitrary kwargs for JSON schema; use `json_schema_extra` for additional schema details.
- Config as Dict: Configuration is now set using a `model_config` dict, replacing the `Config` inner class.
- Type Preservation in Unions: Unions now preserve input types, avoiding unnecessary coercion based on declaration order.
- Optional Fields Clarification: `Optional` fields are explicitly required unless given a default value.
- Regex Engine Shift: Moved to Rust's regex crate for regex operations, dropping some features for performance gains.
- TypeAdapter Introduction: Replaces `parse_obj_as` and `schema_of`, streamlining the handling of arbitrary types.
- JSON Schema Customization: Utilize `GenerateJsonSchema` for detailed JSON schema customization, targeting draft 2020-12 by default.
- BaseSettings Relocation: Now found in `pydantic-settings` package, requiring updates for settings management.
- Constrained Types Replaced: Use `Annotated` with `Field` for defining constrained fields, replacing `Constrained*` types.


### aiosql

All SQL statements are stored in the `sql` under the specific backend's directory.

The `aiosql` library is used for storing, retrieving and executing SQL statements.

The naming convention for SQL statements is as follows:

- Structure:
    - Defined by a SQL comment of the form `- name: <query-name>`.
    - Dashes (-) in the name are turned into underlines (_).
    - Example: `- name: get-all-blogs` becomes the method `.get_all_blogs(conn)`.
    - Comments between name and code will be used a documentation string.
    - Variable substitution is done using `:varname`

- Operators are appended to the query name based on the following rules:
    - No Operator (Default): Executes the query and returns all the results.
    - `^` (Select One): Executes a query and returns the first row of a result set, or None if no results.
    - `$` (Select Value): Executes query and returns the first value of first row of result, or None if no results.
    - `!` (Insert/Update/Delete): Executes SQL without returning any results. Used for insert, update, and delete.
    - `<!` (Insert/Update/Delete Returning): Executes a query and returns values.
    - `*!` (Insert/Update/Delete Many): Bulk executes a SQL statement over all items of a given sequence. 
    - `#` (Execute Scripts): Executes SQL statements as a script, useful for DDL statements like `create table`.

IMPORTANT NOTE: Variable substitution is not possible in executed (i.e. name: script#) DDL scripts.
