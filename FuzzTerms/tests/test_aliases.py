from fuzzterms import Project, db


def test_create_alias_project(alias_project: Project):
    assert alias_project.config.search_flag.is_name_ok
    assert alias_project.config.search_flag.is_alias_ok


def test_acquire_connection(alias_project: Project):
    with db.acquire(alias_project) as conn:
        c = conn.cursor()
        c.execute("SELECT 1")
        assert c.fetchone() == (1,)
