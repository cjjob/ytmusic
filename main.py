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
    to_process = []
    for p in all_playlists:
        if p["title"] in cfg["organise"]:
            to_process.append(p)

    # Step 1:
    # Write the "all" playlist to a file so we never lose track.

    # Step 2:
    # Delete the "TODO" playlist.
    # Then recreate it with all the songs that are in the "all" playlist, but in no other playlist.
