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

## Running restore

Restore a playlist from a snapshot (saved under `out/<playlist_name>.txt`):

```sh
python restore.py <playlist_name>
```
