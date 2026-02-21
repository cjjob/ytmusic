Thanks to [sigma67](https://github.com/sigma67)'s [ytmusicapi](https://github.com/sigma67/ytmusicapi)!

## Setup

```sh
cd {project_root}
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# For development (tests, type-checking, formatting):
pip install -r requirements-dev.txt
```

## Running the tests

```sh
pytest
```

## Running main

```sh
python main.py
```

Main writes each configured playlist to `out/<playlist_name>.txt`. It may also create the following files in the project root in the cases where there are songs matching the criteria:

| File | Meaning |
|------|--------|
| **`extra`** | One YouTube Music watch URL per line. Each URL is a track that appears in at least one of your organise playlists (e.g. "un", "best") but is **not** in your "all" playlist. So your categorised playlists reference tracks that are missing from your main library — you may want to add them to "all" or remove them from the other playlists. |
| **`un_and_more`** | One YouTube Music watch URL per line. Each URL is a track that is in **both** the "un" playlist and at least one other organise playlist. "un" is for reviewed tracks that don’t go into any other playlist; if a track is also in another playlist, it might be worth removing it from "un" or from the other playlist. |

## Running restore

Restore a playlist from a snapshot (saved under `out/<playlist_name>.txt`):

```sh
python restore.py <playlist_name>
```
