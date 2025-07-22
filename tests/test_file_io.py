import pytest


def test_file_print_character1(tmp_path):
    file_path = tmp_path / "file.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        print("\u251c", file=f)


def test_file_print_character2(tmp_path):
    file_path = tmp_path / "file.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        print("├", file=f)
