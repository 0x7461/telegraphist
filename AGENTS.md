# telegraphist — agent guide

Updated: 2026-10-09

Telethon-based Telegram chat archiver: pulls messages, media, reactions, replies and
forwards from your own dialogs into one SQLite database and one static HTML viewer per
entity. Customized fork of [TelegramBackup](https://github.com/N4rr34n6/TelegramBackup);
formerly `gr4mfetch` (renamed 2026-10-01). Two entry points: the interactive upstream
monolith `telegram_backup.py`, and `tg_headless.py`, an additive wrapper that archivist's
`telegram` source backend calls programmatically.

## Where to look

- `README.md` — end-user install, credentials, usage, output layout (canonical for users).
- `tests/test_helpers.py` — executable spec for the pure helpers.
- `PLAN.md` — does not exist yet; create it if this grows past the imperative tier.

## Setup

```sh
uv sync                              # create .venv, install from uv.lock
cp .env.example .env                 # then fill API_ID / API_HASH from https://my.telegram.org
```

Requires uv and Python >=3.12.11 (`.python-version` pins 3.14).

## Commands

```sh
uv run pytest -q                     # 28 tests, offline, no client constructed
uv run python -c "import telethon; print(telethon.__version__)"
uv run python telegram_backup.py     # interactive menu: login, list entities, backup/update
uv run python tg_headless.py --login # one-time interactive login to (re)create the session
uv run python tg_headless.py <channel_id> [--output-dir DIR] [--full] [--no-media]
uv run python tg_headless.py --post MANIFEST.json
```

`telegram_backup.py`, `tg_headless.py --login`, and `--post` all reach the real Telegram
account; see Boundaries.

## Project layout

- `telegram_backup.py` — interactive monolith (upstream lineage): `main()` menu,
  `process_entity()` full pull, `update_entity()` incremental, SQLite schema, CSV export,
  Jinja2 HTML rendering.
- `tg_headless.py` — headless API + CLI over the monolith: `make_client`,
  `resolve_channel`, `backup_channel`, `post_channel`. Imports `telegram_backup` unchanged.
- `template.html` — Jinja2 template for the HTML export.
- `tests/` — pytest. `conftest.py` neutralizes `.env` reads and `output/` creation so an
  import never touches real data.
- `pyproject.toml`, `uv.lock` — deps, managed by uv.
- `.env`, `*.session` — real credentials and a live auth session. Git-ignored.
- `output/`, `reference/` — real backups and scratch material. Git-ignored.

## Config shape

- `.env`: `API_ID` (int), `API_HASH` (str), `SESSION_NAME` (optional). `telegram_backup`
  calls `load_dotenv()` and `exit(1)`s at import when `API_ID`/`API_HASH` are unset.
- Output root is the CWD-relative `OUTPUT_DIR = "output"`, laid out as
  `output/<Users|Channels|Supergroups|Groups>/<id>_<name>/` containing `<name>.db`,
  `<name>.html` and `media/`. `tg_headless.py` re-chdirs to its own directory so
  `template.html` resolves.

## Conventions

- Add headless behavior in `tg_headless.py`, never by editing the monolith's functions —
  it is a fork and every upstream rebase conflicts on a changed hunk.
- Run `uv run pytest -q` before committing. The covered helpers are `sanitize_filename`,
  `extract_user_id`, `get_emoji_string` and `get_entity_type`.
- Dependencies go through uv (`uv add`), never pip; commit `uv.lock`.

## Schema

`output/<Type>/<id>_<name>/<name>.db`, one database per entity.

- `messages` — one row per message per entity; `PRIMARY KEY (id, entity_id)`. `id` is
  Telegram's per-chat message id, so `entity_id` is load-bearing in the key. `from_id` is
  Telethon's raw peer string; `user_id` is the id extracted from it by `extract_user_id`.
  `reactions` and `web_preview` are JSON text. `media_file` is a path under `media/`;
  `media_hash` is the file's MD5 (`get_file_hash`), reused to skip re-downloads.
- `buttons`, `replies`, `reactions` — one row per button / reply / reaction, keyed by
  `(message_id, entity_id)` (plus `row, column` or `emoji`).
- Writers: `process_entity()` creates the schema; `update_entity()` is the only other
  writer and migrates old databases in place with `ALTER TABLE` on open. Watermark is
  `MAX(messages.id) WHERE entity_id`. `generate_html()` is the sole read path.

## Boundaries

**Always**

- Run commands through `uv run …` and from the project directory.
- Keep `tg_headless.py` additive.
- Mirror upstream style in `telegram_backup.py`; minimal diffs rebase cleanly.

**Never**

- Open `.env`, `*.session`, `output/` or `reference/` — real credentials, a live auth
  session, and real chat data.
- Run `telegram_backup.py`, `tg_headless.py --login`, `--post` or any backup/update entry
  point from an agent — each connects to the real account.
- `log_out()` from `tg_headless.py` — the session file is shared with archivist; the
  headless paths call `disconnect()` and stop there.
- Construct a `TelegramClient` in tests, or import `telegram_backup` without
  `tests/conftest.py`'s isolation in place.

**Ask first**

- Changing the SQLite schema or `update_entity()`'s watermark — existing backups are
  migrated by ad-hoc `ALTER TABLE`, so a change needs a matching migration branch.
- Rewriting a function in `telegram_backup.py` that upstream owns.

**Untested / known-fragile**

- The interactive `main()` menu, media download, and HTML generation have no tests; only
  the pure helpers are covered.
- `update_entity()` migrates legacy databases in place — untested against a real old
  backup.

## Teardown

- *Local* — remove the session and credentials (`.env`, `*.session`), the venv (`.venv`)
  and the tree (`output/`). `output/` is real backup data: archive it, do not delete it
  blind.
- *Portfolio* — this repo stays standalone; it is archivist's `telegram` source backend,
  so retiring it means retiring that wrapper too (`archivist/PLAN.md`). Close or reopen per
  `~/projects/registry/TOWN.md` `## Closing or reopening a project`.
