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


def write_playlist_to_disk(
    client: YTMusic,
    title: str,
    playlist_id: str,
    sort_write: bool = False,
) -> tuple[set[str], list[SongInfo]]:
    logging.info(f"Writing playlist '{title}' (ID: {playlist_id}) to disk...")
    video_ids: set[str] = set()
    songs: list[SongInfo] = []

    playlist_data: dict[str, Any] = client.get_playlist(
        playlist_id,
        limit=int(1e5),
    )
    tracks: list[dict[str, Any]] = playlist_data["tracks"]
    for track in tracks:
        video_id: str = track["videoId"]
        video_ids.add(video_id)
        songs.append(
            SongInfo(
                title=track["title"],
                artists=[a["name"] for a in track["artists"]],
                video_id=video_id,
            )
        )

    with open(f"out/{title}.txt", "w") as f:
        song_list: list[str] = [
            f"{s.title} :: {', '.join(s.artists)} :: {s.video_id}" for s in songs
        ]
        if sort_write:
            song_list.sort()

        f.write("\n".join(song_list))

    return video_ids, songs


if __name__ == "__main__":

    logging.debug("Loading config...")
    with open("config.yml", "r") as f:
        cfg: dict[str, Any] = yaml.safe_load(f)

    ytmusic: YTMusic = YTMusic(
        "browser.json",
    )

    # Step 1: Record playlist state in case we f*ck up.
    all_playlists: list[dict[str, Any]] = ytmusic.get_library_playlists()

    logging.info(f"Found {len(all_playlists)} playlists.")

    playlists: dict[str, dict[str, Any]] = dict()
    for p in all_playlists:
        title: str = p["title"]
        if title not in cfg["organise"] and title not in cfg["ignore"]:
            logging.error(f"There's an errant playlist floating around...")
            logging.error(f"Playlist: {title}")
            exit(1)

        if title in cfg["organise"] or title == "TODO":
            playlists[title] = p

    all_video_ids: set[str] = set()
    video_ids_in_playlists_other_than_all: set[str] = set()
    for p_name, p in playlists.items():

        if p_name == "TODO":
            continue

        video_ids: set[str] = set()
        songs: list[SongInfo] = []
        video_ids, songs = write_playlist_to_disk(
            client=ytmusic,
            title=p_name,
            playlist_id=p["playlistId"],
            sort_write=True if p_name == "TODO" else False,
        )
        match p_name:
            case "all":
                all_video_ids = video_ids
            case _:
                video_ids_in_playlists_other_than_all |= video_ids

    # Step 2: Delete and recreate the TODO playlist.
    # Based on whatever *manual* playlist additions I've applied.
    # Note, these are down 'outside the code'.
    try:
        todo_playlist_id: str = playlists["TODO"]["playlistId"]
        ytmusic.delete_playlist(todo_playlist_id)
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

    # Finally write out the new TODO playlist.
    # But, note it's not the same unique ID as before.
    # So, need to requery the playlists.
    # Find the playlist with title "TODO" and get its playlistId
    new_todo_playlist_id: str | None = None
    updated_playlists: list[dict[str, Any]] = ytmusic.get_library_playlists()
    for p in updated_playlists:
        if p["title"] == "TODO":
            new_todo_playlist_id = p["playlistId"]
            break
    if new_todo_playlist_id is None:
        raise ValueError('Could not find playlist with title "TODO"!')

    write_playlist_to_disk(
        client=ytmusic,
        title="TODO",
        playlist_id=new_todo_playlist_id,
        sort_write=True,
    )
