"""
MIT License

Copyright (c) 2021-present rqinflow

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import discord
from discord.ext import commands
from typing import Any, Type
import aiohttp
import aiosqlite
from datetime import datetime
import asyncpg
import json

from setup.lists import *
from setup.config import *

TEST_GUILD = discord.Object(id=835495688832811039)

class Context(commands.Context["CloudyBot"]):
    async def send(self, *args: Any, **kwargs: Any) -> discord.Message:
        embed = kwargs.get("embed")
        if embed and not embed.color:
            kwargs["embed"].color = self.bot.embed_color

        for embed in kwargs.get("embeds", []):
            if not embed.color:
                kwargs["embed"].color = self.bot.embed_color

        return await super().send(*args, **kwargs)

class CloudyBot(commands.Bot):
    db: aiosqlite.Connection
    session: aiohttp.ClientSession
    pool: asyncpg.Pool

    def __init__(self):
        intents = discord.Intents(
            guilds=True,
            members=True,
            emojis=True,
            messages=True,
            reactions=True,
            message_content=True,
            presences=True
        )
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            case_insensitive=True,
            status=discord.Status.online,
            activity=discord.Game("@cloudy♡ help"),
            
        )

        self._context: Type[Context]

        self._BotBase__cogs = commands.core._CaseInsensitiveDict()

        self.initial_extensions = {
            "cogs.administration",
            "cogs.autodm",
            "cogs.chroma",
            "cogs.editingstuff",
            "cogs.events",
            "cogs.fun",
            "cogs.help",
            "jishaku",
            "cogs.error_handler",
            "cogs.recruit",
            "cogs.misc",
            "cogs.slash",
            "cogs.imaging",
            "cogs.games",
            "cogs.tags",
            "cogs.levels",
            "cogs.starboard"
        }

    async def get_context(self, message, *, cls=None):
            return await super().get_context(message, cls=cls or Context)

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)

        await self.tree.sync(guild=TEST_GUILD)
        self.session = aiohttp.ClientSession()
        self.webhook = discord.Webhook.from_url(webhook_url, session = aiohttp.ClientSession())
        self.launch_time = datetime.utcnow()
        self.embed_color = 0x2B2D31

        credentials = {"user": postgres_user, "password": postgres_password, "database": postgres_db, "host": postgres_host}
        pool = await asyncpg.create_pool(**credentials)
        async with pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute("CREATE TABLE IF NOT EXISTS user_info (user_id bigint PRIMARY KEY , last_seen timestamp with time zone, online_since timestamp with time zone)")
                await connection.execute("CREATE TABLE IF NOT EXISTS afk (user_id bigint PRIMARY KEY , reason text , time timestamp with time zone)")
                await connection.execute("CREATE TABLE IF NOT EXISTS levels (user_id bigint , guild_id bigint , first_message timestamp with time zone , accent_color text , card_image bytea , messages int , avatar_url text , xp int , username text , inactive boolean , PRIMARY KEY (user_id, guild_id))")
                await connection.execute("CREATE TABLE IF NOT EXISTS inactives (user_id bigint , reason text , month text, PRIMARY KEY(user_id, month))")
                await connection.execute("CREATE TABLE IF NOT EXISTS edits (id SERIAL, username TEXT PRIMARY KEY)")
                await connection.execute("CREATE TABLE IF NOT EXISTS tags (id SERIAL, name TEXT NOT NULL, content TEXT NOT NULL, owner_id BIGINT NOT NULL, guild_id BIGINT NOT NULL, uses INT, created_at TIMESTAMP WITH TIME ZONE, PRIMARY KEY (name, owner_id, guild_id))")
                # await connection.execute("CREATE TABLE IF NOT EXISTS tag_aliases (id SERIAL PRIMARY KEY, alias TEXT NOT NULL, tag_id INT NOT NULL REFERENCES tags (id) ON DELETE CASCADE)")

        dbase = await aiosqlite.connect("recruit.db")
        async with dbase.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS applications (user_id INTEGER PRIMARY KEY, instagram TEXT UNIQUE, accepted INTEGER, msg_id INTEGER, apply_number INTEGER)") 
            await cursor.execute("CREATE TABLE IF NOT EXISTS staff_apps (user_id INTEGER PRIMARY KEY, instagram TEXT UNIQUE, msg_id INTEGER)") 

        self.db = dbase
        self.pool = pool

    async def close(self):
        await self.pool.close()
        await super().close()
        await self.session.close()

    async def on_ready(self):
        print('Cloudy is now online!')

def get_prefix(bot: CloudyBot, message: discord.Message):

    try:
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)

        return prefixes[str(message.guild.id)]
        
    except AttributeError:
        return '+'