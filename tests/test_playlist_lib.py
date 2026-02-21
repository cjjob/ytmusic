"""Tests for playlist_lib snapshot parsing and loading."""

import os
from pathlib import Path

import pytest

from playlist_lib import SongInfo, load_snapshot, parse_snapshot_line


class TestParseSnapshotLine:
    def test_parses_valid_line(self) -> None:
        line = "Song Title :: Artist1, Artist2 :: dQw4w9WgXcQ"
        got = parse_snapshot_line(line)
        assert got == SongInfo(
            title="Song Title",
            artists=["Artist1", "Artist2"],
            video_id="dQw4w9WgXcQ",
        )

    def test_parses_single_artist(self) -> None:
        line = "Hello :: Adele :: YQHsXMglC9A"
        got = parse_snapshot_line(line)
        assert got.title == "Hello"
        assert got.artists == ["Adele"]
        assert got.video_id == "YQHsXMglC9A"

    def test_strips_whitespace_around_line(self) -> None:
        line = "  Title :: A, B :: abc123  "
        got = parse_snapshot_line(line)
        assert got.title == "Title"
        assert got.artists == ["A", "B"]
        assert got.video_id == "abc123"

    def test_strips_artist_names(self) -> None:
        line = "T ::  A ,  B  , C :: vid"
        got = parse_snapshot_line(line)
        assert got.artists == ["A", "B", "C"]

    def test_title_and_video_id_may_contain_separator_if_not_split(self) -> None:
        # Only " :: " (space-colon-colon-space) is the separator
        line = "Title :: One :: v1"
        got = parse_snapshot_line(line)
        assert got.title == "Title"
        assert got.artists == ["One"]
        assert got.video_id == "v1"

    def test_raises_on_empty_line(self) -> None:
        with pytest.raises(ValueError, match="Empty line"):
            _ = parse_snapshot_line("")
        with pytest.raises(ValueError, match="Empty line"):
            _ = parse_snapshot_line("   \n\t  ")

    def test_raises_on_too_few_parts(self) -> None:
        with pytest.raises(ValueError, match="Malformed snapshot line"):
            _ = parse_snapshot_line("Only Title")
        with pytest.raises(ValueError, match="Malformed snapshot line"):
            _ = parse_snapshot_line("Title :: Artist")

    def test_raises_on_too_many_parts(self) -> None:
        with pytest.raises(ValueError, match="Malformed snapshot line"):
            _ = parse_snapshot_line("A :: B :: C :: D")


class TestLoadSnapshot:
    def test_loads_file_and_returns_songs(self, tmp_path: Path) -> None:
        (tmp_path / "out").mkdir()
        _ = (tmp_path / "out" / "myplaylist.txt").write_text(
            "First :: A1 :: id1\nSecond :: B1, B2 :: id2\n"
        )
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            got = load_snapshot("myplaylist")
        finally:
            os.chdir(orig_cwd)
        assert len(got) == 2
        assert got[0] == SongInfo("First", ["A1"], "id1")
        assert got[1] == SongInfo("Second", ["B1", "B2"], "id2")

    def test_skips_blank_lines(self, tmp_path: Path) -> None:
        (tmp_path / "out").mkdir()
        _ = (tmp_path / "out" / "p.txt").write_text(
            "One :: X :: v1\n" + "\n" + "  \n" + "Two :: Y :: v2\n"
        )
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            got = load_snapshot("p")
        finally:
            os.chdir(orig_cwd)
        assert len(got) == 2
        assert got[0].video_id == "v1"
        assert got[1].video_id == "v2"

    def test_raises_file_not_found_when_file_missing(self, tmp_path: Path) -> None:
        (tmp_path / "out").mkdir()
        # no myplaylist.txt
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(FileNotFoundError, match="Snapshot file.*not found"):
                _ = load_snapshot("myplaylist")
        finally:
            os.chdir(orig_cwd)

    def test_raises_file_not_found_when_out_dir_missing(self, tmp_path: Path) -> None:
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(FileNotFoundError, match="Snapshot file.*not found"):
                _ = load_snapshot("anything")
        finally:
            os.chdir(orig_cwd)

    def test_raises_on_malformed_line_with_line_number(self, tmp_path: Path) -> None:
        (tmp_path / "out").mkdir()
        _ = (tmp_path / "out" / "bad.txt").write_text(
            "Good :: Artist :: id1\n" + "Bad line\n"
        )
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(ValueError, match="Error parsing snapshot line 2"):
                _ = load_snapshot("bad")
        finally:
            os.chdir(orig_cwd)

    def test_returns_empty_list_for_file_with_only_blank_lines(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / "out").mkdir()
        _ = (tmp_path / "out" / "empty.txt").write_text("\n\n  \n")
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            got = load_snapshot("empty")
        finally:
            os.chdir(orig_cwd)
        assert got == []
