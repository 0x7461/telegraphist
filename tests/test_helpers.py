"""Tests for the pure helpers in telegram_backup.

Synthetic inputs only: telethon TL types are constructed offline (no network,
no client), and SimpleNamespace stands in for objects with a ``reaction``
attribute. See conftest.py for the import-time isolation.
"""

import datetime
from types import SimpleNamespace

import pytest
from telethon.tl.types import (
    Channel,
    ChannelForbidden,
    Chat,
    ReactionCustomEmoji,
    ReactionEmoji,
    ReactionPaid,
    User,
)

from telegram_backup import (
    extract_user_id,
    get_emoji_string,
    get_entity_type,
    sanitize_filename,
)

_DATE = datetime.datetime(2020, 1, 1)


def _channel(*, broadcast=False, megagroup=False):
    return Channel(
        id=1, title="chan", broadcast=broadcast, megagroup=megagroup, photo=None, date=_DATE
    )


# --------------------------------------------------------------------------- #
# sanitize_filename
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("plain_name-1.2.txt", "plain_name-1.2.txt"),  # allowed chars pass through
        ("a/b\\c:d*e?f", "a_b_c_d_e_f"),               # illegal chars -> underscore
        ("caf\u00e9_\u65e5\u672c.png", "caf\u00e9_\u65e5\u672c.png"),  # \w is unicode-aware
        ("chat \U0001f525.json", "chat _.json"),        # emoji -> single underscore
        ("../../etc/passwd", ".._.._etc_passwd"),       # path separators neutralized
    ],
)
def test_sanitize_filename(raw, expected):
    assert sanitize_filename(raw) == expected


# --------------------------------------------------------------------------- #
# extract_user_id
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "raw, expected",
    [
        (None, None),
        ("", None),
        ("PeerUser(user_id=12345)", "12345"),
        ("PeerChannel(channel_id=67890)", "67890"),
        ("PeerChat(chat_id=111)", "111"),
        ("12345", "12345"),                             # bare numeric id
        ("not-an-id", None),
        ("user_id=1 channel_id=2", "1"),                # user_id takes precedence
    ],
)
def test_extract_user_id(raw, expected):
    assert extract_user_id(raw) == expected


# --------------------------------------------------------------------------- #
# get_entity_type
# --------------------------------------------------------------------------- #

def test_get_entity_type_user():
    assert get_entity_type(User(id=1)) == "Users"


def test_get_entity_type_broadcast_channel():
    assert get_entity_type(_channel(broadcast=True)) == "Channels"


def test_get_entity_type_megagroup():
    assert get_entity_type(_channel(megagroup=True)) == "Supergroups"


def test_get_entity_type_non_broadcast_channel_is_supergroup():
    assert get_entity_type(_channel()) == "Supergroups"


def test_get_entity_type_chat():
    def _chat():
        return Chat(
            id=4,
            title="grp",
            photo=None,
            participants_count=1,
            date=_DATE,
            version=1,
        )

    assert get_entity_type(_chat()) == "Groups"


def test_get_entity_type_channel_forbidden_is_unknown():
    forbidden = ChannelForbidden(id=5, access_hash=1, title="x", until_date=_DATE)
    assert get_entity_type(forbidden) == "Unknown"


def test_get_entity_type_unknown_object():
    assert get_entity_type(object()) == "Unknown"


# --------------------------------------------------------------------------- #
# get_emoji_string
# --------------------------------------------------------------------------- #

def test_get_emoji_string_emoji_reaction():
    assert get_emoji_string(ReactionEmoji(emoticon="\U0001f44d")) == "\U0001f44d"


def test_get_emoji_string_custom_emoji_document():
    assert get_emoji_string(ReactionCustomEmoji(document_id=123)) == "CustomEmoji:123"


def test_get_emoji_string_plain_string():
    assert get_emoji_string("\U0001f600") == "\U0001f600"


def test_get_emoji_string_emoji_attribute():
    assert get_emoji_string(SimpleNamespace(emoji="\U0001f525")) == "\U0001f525"


def test_get_emoji_string_unwraps_nested_reaction_entity():
    wrapper = SimpleNamespace(reaction=ReactionEmoji(emoticon="\u2764"))
    assert get_emoji_string(wrapper) == "\u2764"


def test_get_emoji_string_unwraps_nested_string():
    assert get_emoji_string(SimpleNamespace(reaction="\U0001f602")) == "\U0001f602"


def test_get_emoji_string_unknown_reaction_falls_back_to_str():
    reaction = ReactionPaid()
    assert get_emoji_string(reaction) == str(reaction)


def test_get_emoji_string_error_guard_returns_unknown():
    class Exploding:
        @property
        def emoticon(self):
            raise ValueError("boom")

    assert get_emoji_string(Exploding()) == "Unknown"
