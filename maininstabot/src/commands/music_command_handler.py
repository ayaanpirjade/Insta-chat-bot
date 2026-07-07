# Music command handler using pyautogui-based UI automation.
# NOTE: This repo does not currently contain UI automation helpers.
# This module implements a minimal, self-contained approach and must be tuned
# with your screen coordinates / image templates before it will work reliably.

from __future__ import annotations

import re
import time
import threading
from dataclasses import dataclass

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore

import config


# Try to use existing logger if present; otherwise fall back to stdlib logging.
try:
    # If your project has a logger module, adapt this import.
    from src import logger as _logger  # type: ignore

    logger = getattr(_logger, "logger", None) or _logger
except Exception:  # pragma: no cover
    import logging

    logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MusicResult:
    ok: bool
    error: str | None = None


class MusicCommandHandler:
    """Handle !play [song] by automating Instagram's sticker/music UI.

    Public API:
        async execute(message) -> bool

    This class is responsible for:
      - parsing the song name
      - per-user cooldown (10 seconds)
      - UI automation:
          open sticker panel
          select Music tab
          search song
          click first result
          send as music sticker
      - fallback message if search fails
      - error logging

    IMPORTANT:
      This is UI automation based on pyautogui. You MUST customize
      coordinates / detection logic to match your screen/device.

    Expected "message" object shape:
      - message.text : incoming text
      - message.user_id : sender user id
      - message.thread_id or message.thread.id : chat id
      - We also assume we can send messages via instagrapi client elsewhere.

    Because the current bot is instagrapi-based and doesn't provide a UI
    automation surface, the sending step is implemented via a callback:
      - message.client_send_music_sticker(music_title) OR
      - message.reply(text) OR
      - message.thread_send(text)

    If none exist, execute() will return False.
    """

    _COOLDOWN_SECONDS = 10
    _SEARCH_TIMEOUT_SECONDS = 5

    def __init__(self):
        self._cooldown_lock = threading.Lock()
        self._last_play_ts: dict[str, float] = {}

    def _parse_song(self, text: str) -> str | None:
        if not text:
            return None
        # Matches: !play song name (case-insensitive)
        m = re.match(r"^!play\s+(.+)$", text.strip(), flags=re.IGNORECASE)
        if not m:
            return None
        song = m.group(1).strip()
        # Avoid empty / too short
        if not song:
            return None
        return song

    def _cooldown_ok(self, user_id: str) -> bool:
        now = time.time()
        with self._cooldown_lock:
            last = self._last_play_ts.get(user_id)
            if last is not None and (now - last) < self._COOLDOWN_SECONDS:
                return False
            self._last_play_ts[user_id] = now
            return True

    async def execute(self, message) -> bool:
        """Execute the !play command.

        Returns:
          True if automation was performed and the sticker was sent.
          False otherwise.
        """
        try:
            text = getattr(message, "text", "") or ""
            user_id = str(getattr(message, "user_id", ""))
            if not user_id:
                return False

            song = self._parse_song(text)
            if not song:
                return False

            if not self._cooldown_ok(user_id):
                # Cooldown silently ignore (or send a message if you prefer)
                return False

            if pyautogui is None:
                await self._reply_text(message, "❌ UI automation dependency not available (pyautogui missing).")
                return False

            # 1) Open sticker panel (bottom-left of input field)
            # TODO: Customize coordinates for your device.
            # Example placeholder coordinates:
            #   - sticker icon center at (x=120, y=890)
            # You must update these values.
            self._open_sticker_panel()

            # 2) Switch to Music tab
            self._select_music_tab()

            # 3) Type song in search bar
            self._type_song(song)

            # 4) Wait for results up to 5 seconds
            got_results = self._wait_for_first_result()
            if not got_results:
                # fallback message
                await self._reply_text(message, f"❌ No results found for {song}")
                return False

            # 5) Click first track result
            self._click_first_track()

            # 6) Send it as a music sticker
            sent = self._send_music_sticker()
            if not sent:
                await self._reply_text(message, f"❌ No results found for {song}")
                return False

            return True

        except Exception as e:
            try:
                logger.exception(f"[MusicCommandHandler] execute failed: {e}")
            except Exception:
                # last resort
                print(f"[MusicCommandHandler] execute failed: {e}")
            return False

    # -------------------- UI Automation (pyautogui) --------------------

    # The following helpers are intentionally written as stubs with clear
    # TODO markers. They need coordinates or image-based detection to work.

    def _open_sticker_panel(self):
        """Click sticker icon at bottom-left of input field."""
        # TODO: Replace with your coordinates.
        x, y = 120, 890
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click()
        time.sleep(0.8)

    def _select_music_tab(self):
        """Switch to Music tab inside sticker panel."""
        # TODO: Replace with your coordinates.
        x, y = 260, 170
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click()
        time.sleep(0.6)

    def _type_song(self, song: str):
        """Enter song name into search bar."""
        # TODO: Replace with your coordinates.
        x, y = 260, 260
        pyautogui.click(x, y)
        # Clear existing query
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)
        pyautogui.typewrite(song, interval=0.02)
        time.sleep(0.3)
        # Optional: press enter to trigger search
        pyautogui.press("enter")
        time.sleep(0.6)

    def _wait_for_first_result(self) -> bool:
        """Wait up to 5 seconds for search results to appear.

        Currently uses a fixed sleep window as placeholder.
        Replace with image detection / pixel check.
        """
        timeout = self._SEARCH_TIMEOUT_SECONDS
        start = time.time()
        while time.time() - start < timeout:
            # TODO: Replace with actual detection.
            # Placeholder: assume results appear after 2 seconds.
            if time.time() - start >= 2.0:
                return True
            time.sleep(0.2)
        return False

    def _click_first_track(self):
        """Click the first matching track result."""
        # TODO: Replace with your coordinates.
        x, y = 290, 420
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click()
        time.sleep(0.6)

    def _send_music_sticker(self) -> bool:
        """Send the selected music sticker."""
        # TODO: Replace with your coordinates.
        # Many Instagram stickers send with a paper-plane/send button.
        # Provide placeholder coordinates for the send button.
        x, y = 340, 920
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click()
        time.sleep(0.8)
        return True

    async def _reply_text(self, message, text: str):
        """Send a text reply.

        The current bot uses instagrapi and sends replies in server.py.
        There is no generic reply method here, so we support multiple
        optional hooks on the message object.
        """
        # If message has a reply coroutine, use it.
        reply_fn = getattr(message, "reply", None)
        if callable(reply_fn):
            try:
                res = reply_fn(text)
                if hasattr(res, "__await__"):
                    await res
                return
            except Exception:
                pass

        # If message has thread_id and a client callback
        thread = getattr(message, "thread", None)
        client_send = getattr(message, "client_send", None)
        if callable(client_send) and thread is not None:
            thread_id = getattr(thread, "id", None)
            if thread_id is not None:
                client_send(thread_id, text)
                return

        # If cannot reply, do nothing.
        return

