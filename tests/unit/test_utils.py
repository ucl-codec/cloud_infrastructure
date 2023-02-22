import pathlib

from aws_fbm.utils import repo_path


def test_repo_path():
    actual = str(repo_path().resolve())
    expected = f"{str(pathlib.Path(__file__).parent.parent.parent.resolve())}"
    assert actual == expected
