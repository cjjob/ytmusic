import logging
import sys
from typing import NoReturn

from playlist_lib import get_playlist_id_by_title, init_client, load_snapshot


logging.basicConfig(level=logging.DEBUG)


def die(message: str, exit_code: int = 1) -> NoReturn:
    logging.error(message)
    raise SystemExit(exit_code)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python restore.py <playlist_name>", file=sys.stderr)
        raise SystemExit(1)

    playlist_name = sys.argv[1]
    logging.info(f"Restoring playlist {playlist_name!r} from snapshot...")

    # Load snapshot file and extract video IDs.
    try:
        songs = load_snapshot(playlist_name)
    except FileNotFoundError:
        die(
            f"Snapshot file for playlist {playlist_name!r} not found at "
            + f"out/{playlist_name}.txt"
        )
    except ValueError as e:
        die(
            f"Failed to parse snapshot file for playlist {playlist_name!r}: {e}"
        )

    video_ids = [s.video_id for s in songs]
    if not video_ids:
        logging.warning(
            f"Snapshot for playlist {playlist_name!r} contained no tracks. "
            + "Resulting playlist will be empty."
        )

    client = init_client()

    # Look up existing playlist by title.
    try:
        playlist_id = get_playlist_id_by_title(client, playlist_name)
    except ValueError as e:
        die(str(e))

    # Delete existing playlist first.
    logging.info(
        f"Deleting existing playlist {playlist_name!r} (ID: {playlist_id})..."
    )
    _ = client.delete_playlist(playlist_id)

    # Recreate playlist with the collected video IDs.
    logging.info(
        f"Recreating playlist {playlist_name!r} with {len(video_ids)} items..."
    )
    _ = client.create_playlist(
        title=playlist_name,
        description="restored from snapshot by restore.py",
        video_ids=video_ids,
    )

    logging.info(f"Successfully restored playlist {playlist_name!r}.")


if __name__ == "__main__":
    main()

