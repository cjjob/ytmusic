import logging
import os

from dotenv import load_dotenv
from ytmusicapi import OAuthCredentials, YTMusic

logging.basicConfig(level=logging.INFO)

load_dotenv()

ytmusic = YTMusic(
    "oauth.json",
    oauth_credentials=OAuthCredentials(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
    ),
)

logging.info(bool(ytmusic))
