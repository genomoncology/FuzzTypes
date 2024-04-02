import sqlite3
from contextlib import contextmanager
from pathlib import Path

import aiosql

from fuzzimport import lazy_import
from .project import Project

sql = aiosql.from_path(Path(__file__).parent / "sql", "sqlite3")


def get_connection(project: Project):
    """
    Establishes and returns a new database connection using Project's
    database path (db_path).

    Returns:
        sqlite3.connection: A new database connection object.
    """

    conn = sqlite3.connect(project.db_path)

    if project.config.search_flag.is_semantic_ok:
        sqlite_vss = lazy_import("sqlite_vss")
        conn.enable_load_extension(True)
        sqlite_vss.load(conn)

    return conn


@contextmanager
def acquire(project: Project, existing_connection=None):
    """
    Context manager for acquiring a database connection. It either uses an
    existing connection passed as an argument or creates a new one. This
    function also manages committing or rolling back transactions.

    If a new connection is created, it's committed and closed automatically
    upon successful execution within the context, or rolled back on exception

    Args:
        project: Terms project object that contains the database path.
        existing_connection (sqlite3.connection, optional): An existing DB
        connection to be used within the context. If None, a new connection
        is created.
        Defaults to None.

    Yields:
        sqlite3.connection: The DB connection to be used within the context.

    Raises:
        Exception: Propagates any exceptions that occur within the context.
    """
    conn = existing_connection

    if conn is None:
        conn = get_connection(project=project)

    try:
        yield conn

        # No exceptions occurred, committing if created in this context
        if not existing_connection:
            conn.commit()

    # Rollback transaction in case of exception
    except Exception as e:  # pragma: no cover
        conn.rollback()
        raise e

    finally:
        # Close connection if it was created in this context
        if not existing_connection:
            conn.close()


# Function to check and initialize the database
def init_database(project: Project):
    with acquire(project) as conn:
        sql.initialize(conn)
