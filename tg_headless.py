"""Headless, importable entry points for telegraphist.

Drives the existing telegram_backup functions (process_entity / update_entity)
without the interactive main() menu, so archiver's `telegram` source backend
can call them programmatically. Purely additive: this module does NOT modify
the upstream monolith, so it never conflicts on an upstream rebase.

Key differences from the interactive tool:
  - resolves a channel by its immutable numeric id (no dialog-menu selection)
  - reuses an existing session (no interactive phone/code login)
  - never logs out and never deletes account service messages
"""

import os
import asyncio
import random

from dotenv import load_dotenv

# Load creds before importing the monolith — its module-level guard calls
# exit(1) on missing API_ID/API_HASH. Explicit path makes this CWD-independent.
_HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_HERE, ".env"))

import telegram_backup as tb  # noqa: E402  (must follow load_dotenv)
from telethon import TelegramClient  # noqa: E402
from telethon.tl.types import PeerChannel  # noqa: E402


def make_client(session=None, api_id=None, api_hash=None, *, receive_updates=False):
    """Build a TelegramClient from an existing session — no interactive login.

    session: Telethon session name/path. Defaults to env SESSION_NAME.
    """
    session = session or os.getenv("SESSION_NAME")
    if not session:
        raise ValueError("no session: pass session= or set SESSION_NAME in .env")
    return TelegramClient(
        session,
        api_id or tb.api_id,
        api_hash or tb.api_hash,
        receive_updates=receive_updates,
    )


async def resolve_channel(client, channel_id):
    """Resolve a channel by numeric id to a Telethon entity.

    Tries the entity cache first (populated by prior backups), then falls back
    to a dialog scan which repopulates access hashes.
    """
    channel_id = int(channel_id)
    try:
        return await client.get_entity(PeerChannel(channel_id))
    except (ValueError, TypeError):
        async for dialog in client.iter_dialogs():
            if dialog.entity.id == channel_id:
                return dialog.entity
        raise LookupError(f"channel id {channel_id} not found in dialogs")


async def backup_channel(client, channel_id, *, output_dir=None, update=True,
                         download_media=True):
    """Headless backup/update of one channel by id into output_dir.

    Reuses telegram_backup.update_entity / process_entity unchanged. Never logs
    out; never deletes service messages. `update=True` is incremental (only
    messages newer than the DB watermark); `update=False` is a full pull.
    """
    if output_dir:
        tb.OUTPUT_DIR = output_dir
        os.makedirs(os.path.join(output_dir, "media"), exist_ok=True)
    entity = await resolve_channel(client, channel_id)
    name = getattr(entity, "title", str(channel_id))
    if update:
        await tb.update_entity(client, entity.id, name, entity,
                               download_media=download_media)
    else:
        await tb.process_entity(client, entity.id, name, entity,
                                download_media=download_media)


async def post_channel(client, channel_id, items, *, gap_min=3.0, gap_max=6.0):
    """Post each item as a document into a channel, with a jittered inter-post gap.

    items: list of {"file": abs-path, "caption": str}. Uses force_document=True so
    original bytes are preserved (photo mode would recompress + strip EXIF). The gap
    between posts is randomized in [gap_min, gap_max] so the feed has no fixed rhythm.
    Returns a per-item result list [{"file", "ok", "message_id"|"error"}] — the caller
    records only genuinely-posted items in its ledger, so a mid-batch failure never desyncs.
    """
    entity = await resolve_channel(client, channel_id)
    results = []
    for i, item in enumerate(items):
        path = item["file"]
        try:
            msg = await client.send_file(
                entity, path, caption=item.get("caption") or "", force_document=True,
            )
            results.append({"file": path, "ok": True, "message_id": msg.id})
        except Exception as e:  # one bad file never aborts the batch
            results.append({"file": path, "ok": False, "error": f"{type(e).__name__}: {e}"})
        if i + 1 < len(items):
            await asyncio.sleep(random.uniform(gap_min, gap_max))
    return results


async def _cli():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Headless telegraphist channel backup")
    parser.add_argument("channel_id", type=int, nargs="?",
                        help="immutable Telegram channel id (omit with --login)")
    parser.add_argument("--login", action="store_true",
                        help="interactive one-time login to (re)create the session, then exit")
    parser.add_argument("--session", default=None,
                        help="Telethon session name/path (default: env SESSION_NAME)")
    parser.add_argument("--output-dir", default=None,
                        help="output root (default: telegram_backup's OUTPUT_DIR)")
    parser.add_argument("--full", action="store_true",
                        help="full pull instead of incremental update")
    parser.add_argument("--no-media", action="store_true", help="skip media download")
    parser.add_argument("--post", metavar="MANIFEST", default=None,
                        help="post mode: JSON manifest {channel_id, items:[{file,caption}]}; "
                             "posts each file as a document, prints POST_RESULTS <json>")
    args = parser.parse_args()

    # Run from the project dir so template.html + default output/ resolve.
    os.chdir(_HERE)

    client = make_client(session=args.session)

    if args.login:
        # Interactive: prompts for phone, then login code, then 2FA if enabled.
        await client.start()
        print("authorized:", await client.is_user_authorized())
        await client.disconnect()
        return

    if args.post:
        with open(args.post) as f:
            manifest = json.load(f)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                raise SystemExit(
                    "session not authorized — run `--login` once to refresh it")
            results = await post_channel(
                client, manifest["channel_id"], manifest["items"],
                gap_min=manifest.get("gap_min", 3.0),
                gap_max=manifest.get("gap_max", 6.0))
        finally:
            await client.disconnect()  # NEVER log_out — session is shared with archiver
        print("POST_RESULTS " + json.dumps(results))
        return

    if args.channel_id is None:
        parser.error("channel_id is required unless --login or --post is given")

    await client.connect()
    try:
        if not await client.is_user_authorized():
            raise SystemExit(
                "session not authorized — run `--login` once to refresh it")
        await backup_channel(
            client, args.channel_id,
            output_dir=args.output_dir,
            update=not args.full,
            download_media=not args.no_media,
        )
    finally:
        await client.disconnect()  # NEVER log_out — the session is shared with archiver


if __name__ == "__main__":
    asyncio.run(_cli())
