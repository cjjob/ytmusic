from typing import Any


from dataclasses import dataclass
import logging
from collections.abc import Collection

import yaml
from ytmusicapi import YTMusic

logging.basicConfig(level=logging.DEBUG)


@dataclass
class SongInfo:
    title: str
    artists: list[str]
    video_id: str


def load_config():
    logging.debug("Loading config...")
    with open("config.yml", "r") as f:
        return yaml.safe_load(f)


def write_playlist_to_disk(
    client: YTMusic,
    title: str,
    playlist_id: str,
) -> tuple[set[str], list[SongInfo]]:
    logging.info(f"Writing playlist '{title}' (ID: {playlist_id}) to disk...")
    video_ids: set[str] = set()
    songs: list[SongInfo] = []

    for track in client.get_playlist(
        playlist_id,
        limit=int(1e5),
    )["tracks"]:
        video_ids.add(track["videoId"])
        songs.append(
            SongInfo(
                title=track["title"],
                artists=[a["name"] for a in track["artists"]],
                video_id=track["videoId"],
            )
        )

    with open(f"out/{title}.txt", "w") as f:
        f.write(
            "\n".join(
                [f"{s.title} :: {', '.join(s.artists)} :: {s.video_id}" for s in songs]
            )
        )

    return video_ids, songs


if __name__ == "__main__":

    cfg = load_config()

    ytmusic = YTMusic(
        "browser.json",
    )

    # Step 1: Record playlist state in case we f*ck up.
    all_playlists = ytmusic.get_library_playlists()

    logging.info(f"Found {len(all_playlists)} playlists.")

    playlists = dict()
    for p in all_playlists:
        if p["title"] not in cfg["organise"] and p["title"] not in cfg["ignore"]:
            logging.error(f"There's an errant playlist floating around...")
            logging.error(f"Playlist: {p['title']}")
            exit(1)

        if p["title"] in cfg["organise"] or p["title"] == "TODO":
            playlists[p["title"]] = p

    all_video_ids = set()
    video_ids_in_playlists_other_than_all = set()
    for p_name, p in playlists.items():
        video_ids, songs = write_playlist_to_disk(
            client=ytmusic,
            title=p_name,
            playlist_id=p["playlistId"],
        )
        match p_name:
            case "all":
                all_video_ids = video_ids
            case "TODO":
                continue
            case _:
                video_ids_in_playlists_other_than_all |= video_ids

    # Step 2: Delete and recreate the TODO playlist.
    # Based on whatever *manual* playlist additions I've applied.
    # Note, these are down 'outside the code'.
    try:
        ytmusic.delete_playlist(playlists["TODO"]["playlistId"])
    except KeyError:
        logging.warning(
            "You probably ran the script wrong previously... "
            "You should investigate if "
            "(1) you didn't expect this warning or "
            "(2) you can't work out why you're seeing it."
        )

    ytmusic.create_playlist(
        title="TODO",
        description="gigachads test in prod",
        video_ids=list(all_video_ids - video_ids_in_playlists_other_than_all),
    )
