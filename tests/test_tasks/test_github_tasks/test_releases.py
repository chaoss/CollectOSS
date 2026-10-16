from collectoss.tasks.github.releases import core


def test_tags_query_returns_none(monkeypatch):
    no_releases = {"data": {"repository": {"id": "R_1", "releases": {"edges": []}}}}
    responses = iter([no_releases, None])
    monkeypatch.setattr(core, "request_graphql_dict", lambda *args, **kwargs: next(responses))

    result = core.releases_model(None, None, logging.getLogger(__name__), "https://github.com/owner/repo", 1)

    assert result is None
