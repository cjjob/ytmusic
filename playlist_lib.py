import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tenacity import retry, stop_after_attempt, wait_fixed
from ytmusicapi import YTMusic


@dataclass
class SongInfo:
    title: str
    artists: list[str]
    video_id: str


def init_client() -> YTMusic:
    """
    Initialise a YTMusic client using the local browser.json.
    """
    return YTMusic("browser.json")


def parse_snapshot_line(line: str) -> SongInfo:
    """
    Parse a single snapshot line of the form:

        {title} :: {artist1, artist2} :: {video_id}
    """
    stripped = line.strip()
    if not stripped:
        raise ValueError("Empty line in snapshot file")

    parts = stripped.split(" :: ")
    if len(parts) != 3:
        raise ValueError(f"Malformed snapshot line: {line!r}")

    title, artists_str, video_id = parts
    artists = [a.strip() for a in artists_str.split(",") if a.strip()]

    return SongInfo(
        title=title,
        artists=artists,
        video_id=video_id,
    )


def load_snapshot(name: str) -> list[SongInfo]:
    """
    Load a playlist snapshot from out/{name}.txt.
    """
    path = Path("out") / f"{name}.txt"
    if not path.is_file():
        raise FileNotFoundError(
            f"Snapshot file for playlist {name!r} not found at {path!s}"
        )

    songs: list[SongInfo] = []
    with path.open("r") as f:
        for idx, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                # Skip blank lines
                continue
            try:
                songs.append(parse_snapshot_line(stripped))
            except ValueError as e:
                raise ValueError(
                    f"Error parsing snapshot line {idx} in {path!s}: {e}"
                ) from e

    return songs


@retry(stop=stop_after_attempt(2), wait=wait_fixed(4))
def get_playlist_id_by_title(client: YTMusic, title: str) -> str:
    """
    Find a playlist by exact title in the user's library.

    - If exactly one match is found, return its playlistId.
    - If none or more than one are found, raise ValueError.
    """
    logging.debug(f"Looking up playlist with title {title!r}...")
    playlists: list[dict[str, Any]] = client.get_library_playlists()

    matches: list[dict[str, Any]] = [p for p in playlists if p.get("title") == title]

    if not matches:
        raise ValueError(f"Could not find playlist with title {title!r}")

    if len(matches) > 1:
        ids = [p.get("playlistId") for p in matches]
        raise ValueError(
            f"Found multiple playlists with title {title!r}: IDs={ids}. "
            "Refusing to choose automatically."
        )

    playlist_id = matches[0].get("playlistId")
    if not playlist_id:
        raise ValueError(
            f"Playlist entry for title {title!r} is missing 'playlistId' field"
        )

    return playlist_id
