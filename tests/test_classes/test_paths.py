from collectoss.application.paths import _build_path, _clean_path
from pathlib import Path

class TestBuildPath:
    def test_build_path(self):
        assert _build_path(None, Path("/path")) == Path("/path")
        assert _build_path("collectoss", Path("/path")) == Path.home() / "collectoss"
        assert _build_path("/collectoss", Path("/path")) == Path("/collectoss")