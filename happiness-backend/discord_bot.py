#!/usr/bin/env python3
"""
Discord bot for the Happiness App: /link and /ask <prompt>

This bot integrates:
- Your backend Discord linking endpoints:
  - POST  /api/discord/link/start
  - GET   /api/discord/link/poll?link_id=...
- Gemini API + MCP (streamable HTTP) tool calling via your Happiness MCP server (/mcp).

Environment variables:
  - DISCORD_BOT_TOKEN            (required)
  - HAPPINESS_BACKEND_BASE_URL   (default: http://localhost:5001)
  - DISCORD_BOT_LINK_SECRET      (optional; must match backend if backend enforces it)
  - GEMINI_API_KEY               (required)
  - GEMINI_MODEL                 (default: gemini-2.5-flash)
  - BOT_DB_PATH                  (default: ./discord_bot.db)

Run:
  source venv/bin/activate
  python discord_bot.py
"""

from __future__ import annotations

import asyncio
import os
import sqlite3
import time
from dataclasses import dataclass
from typing import Optional

import httpx
import discord
from discord import app_commands
from google import genai
from google.genai import types
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

import discord_data


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.environ.get(name)
    return val if val is not None and val != "" else default


DISCORD_BOT_TOKEN = discord_data.discord_token
BACKEND_BASE_URL = (_env("HAPPINESS_BACKEND_BASE_URL",
                    "http://localhost:5001") or "").rstrip("/")
MCP_URL = f"{BACKEND_BASE_URL}/mcp"
BOT_LINK_SECRET = _env("DISCORD_BOT_LINK_SECRET")
# _env("GEMINI_API_KEY")
GEMINI_API_KEY = discord_data.gemini_api_key
GEMINI_MODEL = "gemini-3-flash-preview"

BOT_DB_PATH = _env("BOT_DB_PATH", "./discord_bot.db") or "./discord_bot.db"


def _now_s() -> int:
    return int(time.time())


@dataclass(frozen=True)
class StoredToken:
    access_token: str
    expires_at: int

    @property
    def is_valid(self) -> bool:
        return bool(self.access_token) and self.expires_at > (_now_s() + 60)


class TokenStore:
    """
    Tiny SQLite token store for the bot (discord_user_id -> MCP access token).
    """

    def __init__(self, path: str):
        self.path = path
        self._lock = asyncio.Lock()
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.path, isolation_level=None, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_db(self) -> None:
        conn = self._conn()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS discord_tokens (
                  discord_user_id TEXT PRIMARY KEY,
                  access_token TEXT NOT NULL,
                  expires_at INTEGER NOT NULL
                )
                """
            )
        finally:
            conn.close()

    async def upsert(self, discord_user_id: str, token: StoredToken) -> None:
        async with self._lock:
            conn = self._conn()
            try:
                conn.execute(
                    """
                    INSERT INTO discord_tokens (discord_user_id, access_token, expires_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(discord_user_id) DO UPDATE SET
                      access_token=excluded.access_token,
                      expires_at=excluded.expires_at
                    """,
                    (discord_user_id, token.access_token, token.expires_at),
                )
            finally:
                conn.close()

    async def get(self, discord_user_id: str) -> Optional[StoredToken]:
        async with self._lock:
            conn = self._conn()
            try:
                row = conn.execute(
                    "SELECT access_token, expires_at FROM discord_tokens WHERE discord_user_id=?",
                    (discord_user_id,),
                ).fetchone()
                if not row:
                    return None
                return StoredToken(access_token=str(row[0]), expires_at=int(row[1]))
            finally:
                conn.close()


async def run_gemini_with_mcp_tool(
    *,
    gemini_api_key: str,
    model: str,
    prompt: str,
    mcp_url: str,
    mcp_bearer_token: str,
) -> str:
    """
    Copied/adapted from happiness-backend/gemini_mcp_headless.py:
    Use Gemini with your MCP server as a tool over streamable HTTP.
    """
    ai = genai.Client(api_key=gemini_api_key)

    # IMPORTANT: MCP auth headers belong on the httpx client, not on the MCP transport.
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {mcp_bearer_token}"},
        timeout=httpx.Timeout(30.0, read=60.0 * 5),
    ) as http_client:
        async with streamable_http_client(mcp_url, http_client=http_client) as (
            read_stream,
            write_stream,
            _get_session_id,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await ai.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[session],
                        temperature=0,
                    ),
                )

    return response.text or ""


async def backend_start_link(*, discord_user_id: str) -> tuple[str, str]:
    """
    Returns (link_id, link_url)
    """
    url = f"{BACKEND_BASE_URL}/api/discord/link/start"
    headers = {}
    if BOT_LINK_SECRET:
        headers["X-Bot-Secret"] = BOT_LINK_SECRET
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(url, json={"discord_user_id": discord_user_id}, headers=headers)
        r.raise_for_status()
        body = r.json() or {}
        return str(body["link_id"]), str(body["link_url"])


async def backend_poll_link(*, link_id: str) -> dict:
    url = f"{BACKEND_BASE_URL}/api/discord/link/poll"
    headers = {}
    if BOT_LINK_SECRET:
        headers["X-Bot-Secret"] = BOT_LINK_SECRET
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(url, params={"link_id": link_id}, headers=headers)
        # 404 means expired
        if r.status_code == 404:
            return {"status": "expired"}
        r.raise_for_status()
        return r.json() or {}


class HappinessDiscordBot(discord.Client):
    def __init__(self, token_store: TokenStore):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.token_store = token_store

    async def setup_hook(self) -> None:
        # Register slash commands globally
        await self.tree.sync()


token_store = TokenStore(BOT_DB_PATH)
client = HappinessDiscordBot(token_store=token_store)


@client.tree.command(name="link", description="Link your Happiness App account so I can query your happiness data.")
async def link(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)

    discord_user_id = str(interaction.user.id)

    try:
        link_id, link_url = await backend_start_link(discord_user_id=discord_user_id)
    except Exception as e:
        await interaction.followup.send(f"Failed to start linking: {e}", ephemeral=True)
        return

    await interaction.followup.send(
        "Click this link to sign in and link your Happiness App account:\n"
        f"{link_url}\n\n"
        "After you finish, I’ll confirm here.",
        ephemeral=True,
    )

    async def poll_and_store():
        deadline = _now_s() + 600
        while _now_s() < deadline:
            try:
                result = await backend_poll_link(link_id=link_id)
            except Exception:
                await asyncio.sleep(2)
                continue

            status = result.get("status")
            if status == "pending":
                await asyncio.sleep(2)
                continue
            if status == "expired":
                await interaction.followup.send(
                    "Linking session expired. Please run `/link` again.",
                    ephemeral=True,
                )
                return
            if status == "complete":
                access_token = str(result.get("access_token") or "")
                expires_in = int(result.get("expires_in") or 0)
                if not access_token:
                    await interaction.followup.send(
                        "Linking completed but no token was returned. Please try again.",
                        ephemeral=True,
                    )
                    return

                expires_at = _now_s() + (expires_in if expires_in > 0 else 86400)
                await token_store.upsert(discord_user_id, StoredToken(access_token, expires_at))
                await interaction.followup.send("✅ Linked successfully! You can now use `/ask`.", ephemeral=True)
                return

            await asyncio.sleep(2)

        await interaction.followup.send("Linking timed out. Please run `/link` again.", ephemeral=True)

    asyncio.create_task(poll_and_store())


@client.tree.command(name="ask", description="Ask Gemini a question (it can use your Happiness MCP tools).")
@app_commands.describe(prompt="What do you want to ask?")
async def ask(interaction: discord.Interaction, prompt: str):
    # Public response (visible to the whole channel)
    await interaction.response.defer(thinking=True)

    if not GEMINI_API_KEY:
        await interaction.followup.send("Bot is missing GEMINI_API_KEY.")
        return

    discord_user_id = str(interaction.user.id)
    token = await token_store.get(discord_user_id)
    if not token or not token.is_valid:
        await interaction.followup.send(
            "You’re not linked yet (or your token expired). Run `/link` first."
        )
        return

    try:
        text = await run_gemini_with_mcp_tool(
            gemini_api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
            prompt=prompt,
            mcp_url=MCP_URL,
            mcp_bearer_token=token.access_token,
        )
    except Exception as e:
        await interaction.followup.send(f"Error while calling Gemini/MCP: {e}")
        return

    # Discord message limit is 2000 chars; chunk if needed.
    if not text:
        await interaction.followup.send("(No response text returned.)")
        return

    chunks = [text[i:i + 1900] for i in range(0, len(text), 1900)]
    for idx, chunk in enumerate(chunks):
        await interaction.followup.send(chunk if idx == 0 else f"(cont.) {chunk}")


def main() -> int:
    token = DISCORD_BOT_TOKEN  # _env("DISCORD_BOT_TOKEN")
    if not token:
        print("Missing DISCORD_BOT_TOKEN.")
        return 2
    if not BACKEND_BASE_URL:
        print("Missing HAPPINESS_BACKEND_BASE_URL.")
        return 2
    client.run(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
