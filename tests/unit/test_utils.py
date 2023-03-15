import pathlib

from aws_fbm.utils.utils import repo_path, bool_to_str


def test_repo_path():
    actual = str(repo_path().resolve())
    expected = f"{str(pathlib.Path(__file__).parent.parent.parent.resolve())}"
    assert actual == expected


def test_bool_to_str():
    assert bool_to_str(True) == "True"
    assert bool_to_str(False) == "False"
