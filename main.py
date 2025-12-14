import logging
import yaml
from ytmusicapi import YTMusic

logging.basicConfig(level=logging.DEBUG)


def load_config():
    logging.debug("Loading config...")
    with open("config.yml", "r") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":

    cfg = load_config()

    ytmusic = YTMusic(
        "browser.json",
    )

    all_playlists = ytmusic.get_library_playlists()

    print(len(all_playlists))

    # Loop 1: check if we should even proceed.
    for p in all_playlists:
        if p["title"] not in cfg["organise"] and p["title"] not in cfg["ignore"]:
            logging.error(f"There's an errant playlist floating around...")
            logging.error(f"Playlist: {p['title']}")
            exit(1)

    # Loop 2: filter the relevant playlists.
    # Yes, this could be 1 loop. This also isn't NASA.
    # We're not solving for performance.
    to_process = dict()
    for p in all_playlists:
        if p["title"] in cfg["organise"]:
            to_process[p["title"]] = p

    # Write the "all" playlist to a file so we never lose track.
    all_titles_and_artists = []
    for track in ytmusic.get_playlist(
        to_process["all"]["playlistId"],
        limit=int(1e5),
    )["tracks"]:
        title = track["title"]
        artists = [a["name"] for a in track["artists"]]
        all_titles_and_artists.append(f"{title} :: {', '.join(artists)}")

    with open("out/all.txt", "w") as f:
        f.write("\n".join(all_titles_and_artists))

    # Write the other playlists to while we're at it.

    # Step 2:
    # Delete the "TODO" playlist.
    # Then recreate it with all the songs that are in the "all" playlist, but in no other playlist.
