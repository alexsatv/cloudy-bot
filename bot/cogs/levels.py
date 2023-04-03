import discord
from discord.ext import commands
import random
from typing import Optional, TypedDict, Union
from easy_pil import Canvas, Editor, Font, load_image
from io import BytesIO
import functools
import re
import datetime
from PIL import Image, ImageEnhance, ImageFilter, UnidentifiedImageError
from setup.config import *

class ActivityLevel(TypedDict):
    user_id: int
    guild_id: int
    xp: int
    accent_color: str  
    card_image: str
    messages: int

class Inactivity(TypedDict):
    id: int
    reason: str
    month: str

class Levels(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 2, commands.BucketType.user)
        self.regex_hex = "^#(?:[0-9a-fA-F]{3}){1,2}$"
        self.guilds = [694010548605550675, 835495688832811039]
        self.counting_channels = [694010549532360726, 1070796927840559124, 1077569961289072701, 836647673595428925, 1005863199540793415]

    def private_only():
        def predicate(ctx):
            if ctx.guild.id == 694010548605550675:
                return True
            else:
                return False
        return commands.check(predicate)
    
    def chroma_command():
        def predicate(ctx):
            guilds = [694010548605550675, 835495688832811039]
            if ctx.guild.id in guilds:
                return True
            else:
                return False
        return commands.check(predicate)

    async def get_member(self, member_id: int, guild_id: int) -> Optional[ActivityLevel]:
        query = "SELECT user_id, xp, accent_color, card_image, messages FROM levels WHERE user_id = $1 and guild_id = $2;"
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                row = await connection.fetchrow(query, member_id, guild_id)
        await self.bot.pool.release(connection)
        return row

    async def add_member(self, member_id: int, guild_id: int, avatar: str, username: str) -> None:
        query = "INSERT INTO levels (user_id, guild_id, first_message, accent_color, card_image, messages, avatar_url, xp, username) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(query, member_id, guild_id, discord.utils.utcnow(), "#009efa", None, 1, avatar, 25, username)
        await self.bot.pool.release(connection)

    async def update_levels(self, member_id: int, guild_id: int, old_data: ActivityLevel, xp: int) -> None:
        query = '''UPDATE levels SET messages = $1, xp = $2 WHERE user_id = $3 AND guild_id = $4'''
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(query, old_data["messages"] + 1, old_data["xp"] + xp, member_id, guild_id)
        await self.bot.pool.release(connection)

    async def update_messages(self, member_id: int, guild_id: int) -> None:
        query = "UPDATE levels SET messages = messages + 1 WHERE user_id = $1 AND guild_id = $2"
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(query, member_id, guild_id)
        await self.bot.pool.release(connection)

    async def get_rank(self, member_id: int, guild_id: int) -> int:
        query = '''SELECT COUNT(*) FROM levels WHERE xp > (SELECT xp FROM levels WHERE user_id = $1 AND guild_id = $2) AND guild_id = $2'''
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                rank = await connection.fetchval(query, member_id, guild_id)
        await self.bot.pool.release(connection)
        return rank + 1
    
    async def register_ia(self, member_id: int, reason: str, month: str) -> None:
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                query = "INSERT INTO inactives (user_id, reason, month) VALUES ($1, $2, $3) ON CONFLICT (user_id, month) DO UPDATE SET reason = $2"
                await connection.execute(query, member_id, reason, month)
        await self.bot.pool.release(connection)

    async def get_ia(self, member_id: int) -> Optional[Inactivity]:
        query = "SELECT user_id, reason, month FROM inactives WHERE user_id = $1 AND month = $2;"
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                row = await connection.fetchrow(query, member_id)
        await self.bot.pool.release(connection)
        return row

    async def change_color(self, color: str, member_id: int, guild_id: int) -> None:
        query = "UPDATE levels SET accent_color = $1 WHERE user_id = $2 AND guild_id = $3"
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(query, color, member_id, guild_id)
        await self.bot.pool.release(connection)

    async def set_card_image(self, image: BytesIO, member_id: int, guild_id: int) -> None:
        query = "UPDATE levels SET card_image = $1 WHERE user_id = $2 AND guild_id = $3"
        bytes_data = image.getvalue()
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(query, bytes_data, member_id, guild_id)
        await self.bot.pool.release(connection)

    def make_rank_card(self, member: discord.Member, rank: int, data: ActivityLevel) -> BytesIO:

        xp = data["xp"]
        lvl = 0

        while True:
            if xp < ((50*(lvl**2))+(50*(lvl-1))):
                break
            lvl += 1

        next_level_xp = ((50*(lvl**2))+(50*(lvl-1)))
        xp_need = next_level_xp
        xp_have = xp

        percentage = int(((xp_have * 100)/ xp_need))

        if percentage < 1:
            percentage = 0

        profile_image = load_image(str(member.display_avatar.url))
        profile = Editor(profile_image).resize((250, 250)).circle_image()
    
        poppins_big = Font.poppins(size=117)
        poppins = Font.poppins(size=67)
        poppins_small = Font.poppins(size=50)

        card_right_shape = [(1000, 0), (1250, 500), (1500, 500), (1500, 0)]

        if data["card_image"]:
            b_img = Image.open(BytesIO(data["card_image"]))
            aspect_ratio = b_img.size[0] / b_img.size[1]
            if aspect_ratio > 3:
                new_width = int(img.height * 3)
                img = img.crop(((img.width - new_width) / 2, 0, (img.width + new_width) / 2, img.height))
            elif aspect_ratio < 3:
                new_height = int(b_img.width / 3)
                b_img = b_img.crop((0, (b_img.height - new_height) / 2, b_img.width, (b_img.height + new_height) / 2))
            b_img = b_img.resize((1500, 500))
            enhancer = ImageEnhance.Brightness(b_img)
            b_img = enhancer.enhance(0.8)
            blur = b_img.filter(ImageFilter.GaussianBlur(radius=1.5))
            background = Editor(blur)
        else:
            background = Editor(Canvas((1500, 500), color="#23272A"))
            background.polygon(card_right_shape, "#2C2F33")
        background.text((1225, 192), f"#{str(rank)}", font=poppins_big, color=data["accent_color"])
        background.paste(profile, (50, 50))

        background.rectangle((50, 367), width=1083, height=67, fill="#494b4f", radius=33)
        background.bar(
            (50, 367),
            max_width=1083,
            height=67,
            percentage=percentage,
            fill=data["accent_color"],
            radius=33,
        )
        background.text((333, 67), member.name, font=poppins, color="white")

        background.rectangle((333, 167), width=583, height=3, fill=data["accent_color"])
        background.text(
            (333, 217),
            f"Level {lvl}"
            + f" | {xp} / {xp_need} XP",
            font=poppins_small,
            color="white",
        )

        return background.image_bytes

    async def check_member(self, member: discord.Member) -> bool:
        member_server: discord.Guild = self.bot.get_guild(694010548605550675)
        if member_server in member.mutual_guilds:
            return True
        else:
            return False

    async def level_check(self, message: discord.Message, xp: int, xp_to_add: int) -> None:
        new_xp = xp + xp_to_add
        lvl = 0
        while True:
            if xp < ((50*(lvl**2))+(50*(lvl-1))):
                break
            lvl += 1
        next_level_xp = ((50*(lvl**2))+(50*(lvl-1)))
        if new_xp > next_level_xp: # author has leveled up
            await message.channel.send(f"good job {message.author.mention}, you advanced to **level {lvl+1}** :)")

    async def public_level_handler(self, message: discord.Message, data: Union[ActivityLevel, None], xp_to_add: int, retry_after: Union[float, None]) -> None:
        if data == None: # author isn't in database so we add them
            await self.add_member(message.author.id, message.guild.id, message.author.display_avatar.url, message.author.name + "#" + message.author.discriminator)
        else: # the author is in database so we just need to update their entry
            if retry_after: # they're on cooldown so we just update their message count
                await self.update_messages(message.author.id, message.guild.id)
            else: # not on cooldown so we add xp and update message count
                await self.update_levels(message.author.id, message.guild.id, data, xp_to_add)
                # this checks if they leveled up
                await self.level_check(message, data["xp"], xp_to_add)

    async def public_member_level_handler(self, message: discord.Message, member_data: Union[ActivityLevel, None], data: Union[ActivityLevel, None], retry_after: Union[float, None], xp_to_add: int) -> None:
        if member_data != None or data != None: # one of the databases contain the member
            if member_data != None and data != None:  # member is in both databases
                # update levels
                if retry_after:
                    await self.update_messages(member_id=message.author.id, guild_id=message.guild.id)
                    await self.update_messages(member_id=message.author.id, guild_id=694010548605550675)
                else:
                    await self.update_levels(message.author.id, message.guild.id, data, xp_to_add)
                    await self.update_levels(message.author.id, 694010548605550675, member_data, xp_to_add)
                    # check if they leveled up
                    await self.level_check(message, data["xp"], xp_to_add)
            elif data is not None: # member has public levels only so we need to add private levels
                await self.add_member(message.author.id, 694010548605550675, message.author.display_avatar.url, message.author.name + "#" + message.author.discriminator)
                # update levels, but only public because we added private xp while registering
                if retry_after:
                    await self.update_messages(member_id=message.author.id, guild_id=message.guild.id)
                else:
                    await self.update_levels(message.author.id, message.guild.id, data, xp_to_add)
                    # check if they leveled up
                    await self.level_check(message, data["xp"], xp_to_add)
            elif member_data is not None: # member has private levels only so we need to add public levels
                await self.add_member(message.author.id, message.guild.id, message.author.display_avatar.url, message.author.name + "#" + message.author.discriminator)
                # update levels, but only private because we added public xp while registering
                if retry_after:
                    await self.update_messages(member_id=message.author.id, guild_id=694010548605550675)
                else:
                    # we don't need to check for level up here
                    # that's because if they are leveling up
                    # it's the private levels and that would
                    # just be very confusing to mention here 
                    await self.update_levels(message.author.id, 694010548605550675, data, xp_to_add)
        else: # member hasn't been registered yet
            await self.add_member(message.author.id, 694010548605550675, message.author.display_avatar.url, message.author.name + "#" + message.author.discriminator)
            await self.add_member(message.author.id, message.guild.id, message.author.display_avatar.url, message.author.name + "#" + message.author.discriminator)

    async def private_level_handler(self, message: discord.Message, data: Union[ActivityLevel, None], retry_after: Union[float, None], xp_to_add: int) -> None:
        if data is not None: # member is registered in levels
            if retry_after:
                await self.update_messages(member_id=message.author.id, guild_id=message.guild.id)
            else:
                await self.update_levels(message.author.id, message.guild.id, data, xp_to_add)
                # check if they leveled up
                await self.level_check(message, data["xp"], xp_to_add)
        else: # member hasn't been registered yet
            await self.add_member(message.author.id, message.guild.id, message.author.display_avatar.url, message.author.name + "#" + message.author.discriminator)

    async def handle_message(self, message: discord.Message):

        if message.author.bot is True: 
            return # author is a bot and don't want to add xp to bots

        if message.guild.id not in self.guilds:
            return # message wasn't sent in a chroma guild so we can ignore it
        
        if message.channel.id not in self.counting_channels:
            return # we only want to add xp in certain channels and message wasn't sent in one of them

        bucket = self.cd_mapping.get_bucket(message)
        retry_after = bucket.update_rate_limit()

        is_member = None

        if message.guild.id == 835495688832811039: # message was sent in public
            is_member = await self.check_member(message.author) # checks if the author is a member
            if is_member:
                member_data = await self.get_member(message.author.id, 694010548605550675)

        data = await self.get_member(message.author.id, message.guild.id)
        xp_to_add = random.randint(8, 25)

        if is_member is False: # handles levels for public guild members
            await self.public_level_handler(message, data, xp_to_add, retry_after)
        elif is_member is True: # handles levels for chroma member when message is sent in public guild
            await self.public_member_level_handler(message, member_data, data, retry_after, xp_to_add)
        elif is_member is None: # message was sent by member in private server
            await self.private_level_handler(message, data, retry_after, xp_to_add)

        """ async with aiohttp.ClientSession() as session:
            async with session.ws_connect('ws://127.0.0.1:8000/ws') as ws:
                # await for messages and send messages
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        return await ws.send_str('database update!')
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break """

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.handle_message(message)
    
    @commands.group(invoke_without_command=True)
    @chroma_command()
    async def rank(self, ctx: commands.Context, member: Optional[discord.Member]):
        if not member:
            member = ctx.author
        data = await self.get_member(member.id, ctx.guild.id)
        rank = await self.get_rank(member.id, ctx.guild.id)
        make_card = functools.partial(self.make_rank_card, member, rank, data)
        card = await self.bot.loop.run_in_executor(None, make_card)
        await ctx.send(file=discord.File(fp=card,filename="rankcard.png"))

    @rank.command()
    @chroma_command()
    async def color(self, ctx: commands.Context, color: str):
        match = re.search(self.regex_hex, color)
        if match:
            await self.change_color(color, ctx.author.id, ctx.guild.id)
            await ctx.reply("Succesfully changed your rank card image!")
        else:
            await ctx.reply(f"`{color}` is not a valid hex color")

    @rank.command()
    @private_only()
    async def image(self, ctx: commands.Context, link: Optional[str]):
        if link:
            if link.startswith("https://") or link.startswith("http://"):
                try:
                    async with self.bot.session.get(link) as resp:
                        image = BytesIO(await resp.read())
                        image.seek(0)
                except:
                    return await ctx.send("Couldn't get the image from the link you provided.")
            else:
                return await ctx.send("You need to use a https or http URL")
        else:
            if ctx.message.attachments:
                to_edit = ctx.message.attachments[0]
                image = BytesIO(await to_edit.read())
                image.seek(0)
            else:
                return ctx.send("You need to upload an image attachment or add an image url")
        try:
            b_img = Image.open(image)
        except UnidentifiedImageError:
            return await ctx.send("Invalid image.")
        await self.set_card_image(image, ctx.author.id, ctx.guild.id)
        await ctx.reply("Succesfully changed your rank card image!")

    @commands.command(aliases=['levels'])
    @chroma_command()
    async def leaderboard(self, ctx: commands.Context):
        view = discord.ui.View()
        button = discord.ui.Button(label="Click to see the leaderboard", style=discord.ButtonStyle.url, url=f"https://cloudy.rqinflow.com/levels/{ctx.guild.id}")
        view.add_item(button)
        await ctx.reply("Here you go! <:cuteface:756721125399986199>", view=view)

    @discord.app_commands.command(name="inactivity")
    @discord.app_commands.guilds(discord.Object(id=694010548605550675))
    async def inactive(self, interaction: discord.Interaction, reason: str):
        """Handles monthly inactivity"""
        await interaction.response.defer(ephemeral=True)
        channel = self.bot.get_channel(849707778380922910)
        current_month = datetime.datetime.now().strftime("%B")
        await self.register_ia(interaction.user.id, reason, current_month)
        embed = discord.Embed(title="inactivity", description=f"{reason}", color=0x32D052)
        embed.set_footer(text=f"message from: {interaction.user.display_name}")
        await channel.send(embed=embed)
        await interaction.followup.send("Registered your inactivity")

async def setup(bot: commands.Bot):
    await bot.add_cog(Levels(bot))