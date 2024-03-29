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
import random
import asyncio
from imgurpython import ImgurClient
import pytz
from setup.lists import *
from setup.config import *
import aiohttp
from utils.functions import gif_embed
import typing
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from colorthief import ColorThief
import datetime
from time import strftime, gmtime
import functools
from typing import Optional
from utils.subclasses import Context
from urllib.parse import quote_plus
from utils.muma import LyricsFinder, Track

imgur = ImgurClient(imgur_id, imgur_secret)

class SpotifyView(discord.ui.View):
    def __init__(self, spotify_url: str):
        super().__init__()
        self.add_item(discord.ui.Button(emoji="<:spotify:1090609567639019611>", label='Listen on Spotify', url=spotify_url))

class Fun(commands.Cog, name="Fun", description="Includes commands you can use for fun!"):
    def __init__(self, bot):
        self.bot = bot

    def spotify_card(self, member: discord.Member, album: str) -> BytesIO:
        """Generate a Spotify Card for a member"""
        spotify = discord.utils.find(lambda a: isinstance(a, discord.Spotify), member.activities)
        ct = ColorThief(album)
        colors = ct.get_palette(4, 1)

        font = ImageFont.truetype("Karla-Bold.ttf", 60)
        font2 = ImageFont.truetype("Karla-Bold.ttf", 25)
        image = Image.new("RGBA", (1080, 400), colors[0])

        duration = spotify.duration.seconds
        duration1 = strftime("%M:%S", gmtime(spotify.duration.seconds))
        start = spotify.start
        current = datetime.datetime.now(datetime.timezone.utc)
        test = current - start
        time_left = duration - test.seconds
        time_along = duration - time_left
        duration2 = strftime("%M:%S", gmtime(time_along))
        full_time_percent = duration / 100
        left_of_current = time_along / full_time_percent
        artists = spotify.artist.split(";")

        if len(spotify.title) > 20:
            title = spotify.title[0:15] + "..." 
        else:
            title = spotify.title
        if len(spotify.artist) > 20 and len(artists) > 1:
            artist = artists[0][0:15] + "..." if len(artists[0]) > 20 else artists[0]
        else:
            artist = ", ".join(artists) if len(artists) > 1 else spotify.artist
            artist = artist[0:15] + "..." if len(artist) > 20 else artist
        ImageDraw.Draw(image).text((20,30), f"{title}\n{artist}", colors[1], font=font)
        ImageDraw.Draw(image).line([(20, 200), (600, 200)], fill=colors[1], width=5)
        ImageDraw.Draw(image).text((20,220), f"{duration2}", colors[1], font=font2)
        ImageDraw.Draw(image).text((535,220), f"{duration1}", colors[1], font=font2)
        circle_1 = Image.open("./assets/new_circle.png").convert("RGBA")
        alpha = circle_1.getchannel('A')
        circle_3 = Image.new('RGBA', circle_1.size, color=colors[1])
        circle_3.putalpha(alpha) 
        circle = circle_3.resize((25, 25))
        ttt = left_of_current / 100 * 590
        image.paste(circle, (int(ttt), 188), circle)
        mask = Image.open("./assets/round-corners.png").convert("RGBA")
        mask = mask.resize((300, 300))
        mask_alpha = mask.getchannel('A')
        to_paste = Image.open(album)
        to_paste = to_paste.resize((300, 300))
        image.paste(to_paste, (700, 50), mask_alpha)
        buffer = BytesIO()
        image.save(buffer, "png")
        buffer.seek(0)
        return buffer

    @commands.command()
    async def spotify(self, ctx: Context, member: Optional[discord.Member]):
        """Get a spotify card for the song currently playing
        
        Parameters
        -----------
        member: discord.Member, optional
            the member to get spotify activity from
        """
        async with ctx.typing():
            if not member:
                member = ctx.author
            spotify = discord.utils.find(lambda a: isinstance(a, discord.Spotify), member.activities)
            if not spotify:
                return await ctx.send("This user is not listening to Spotify")
            url = spotify.album_cover_url
            response = await self.bot.session.get(url)
            album = BytesIO(await response.read())
            album.seek(0)
            spotify_card = functools.partial(self.spotify_card, member, album)
            card = await self.bot.loop.run_in_executor(None, spotify_card)
            await ctx.send(file=discord.File(fp=card, filename="spotify.png"), view=SpotifyView(spotify.track_url))

    @commands.command()
    async def hug(self, ctx: Context, member: typing.Optional[discord.Member]):
        """Hug your friends or have Cloudy give you a hug
        
        Parameters
        -----------
        member: discord.Member, optional
            the friend you wanna hug
        """
        author = ctx.message.author.mention
        if member == None:
            await ctx.send(f"Cloudy gave {author} a hug <:bearhug:800042518477013053>")
        else:
            embed = discord.Embed(description=f"{author} gave {member.mention} a hug!", color=0x9A5FF2)
            urls = ['https://cdn.discordapp.com/attachments/804482120671821865/814085524548878346/download_1.gif', "https://cdn.discordapp.com/attachments/804482120671821865/814083420194996224/download.gif", "https://cdn.discordapp.com/attachments/804482120671821865/814086607997108254/tenor.gif", "https://cdn.discordapp.com/attachments/804482120671821865/814087205039243274/tenor_1.gif", "https://cdn.discordapp.com/attachments/804482120671821865/814087528906620968/tenor_2.gif"]
            embed.set_image(url=(random.choice(urls)))
            await ctx.send(embed=embed)

    @commands.command()
    async def hbd(self, ctx: Context, member: typing.Optional[discord.Member]):
        """Wish your friends a happy birthday or have Cloudy wish you a hbd
        
        Parameters
        -----------
        member: discord.Member, optional
            the birthday kid
        """
        author = ctx.message.author
        if member == None:
            await ctx.send(f"Cloudy wishes {author.mention} a happy birthday! <:cake:804020293416517672>")
        else:
            await ctx.send(f'Happy birthday {member.mention}! <:cake:804020293416517672>')
    
    @commands.command()
    async def kiss(self, ctx: Context, member: typing.Optional[discord.Member]):
        """Kiss the homies good night or get a kiss from Cloudy
        
        Parameters
        -----------
        member: discord.Member, optional
            your lover (or the friend you secretly wanna kiss)
        """
        author = ctx.message.author.mention
        kiss = self.bot.get_emoji(804022318992719922)
        if member == None:
            await ctx.reply(f"Cloudy kissed {author}! {kiss}")
        else:
            embed = discord.Embed(description=f"{author} kissed {member.mention} <3 i ship!")
            hugs = ['https://cdn.discordapp.com/attachments/804482120671821865/814095974611681280/37f9f27715e7dec6f2f4b7d63ad1af13.gif', 'https://cdn.discordapp.com/attachments/804482120671821865/814096796582019082/39fe167bdab90223bcc890bcb067b761.gif', 'https://cdn.discordapp.com/attachments/804482120671821865/814097411525836851/5f5afb51884af7c58e8d46c90261f990.gif', 'https://cdn.discordapp.com/attachments/804482120671821865/814097832494759936/tenor_1.gif', 'https://cdn.discordapp.com/attachments/804482120671821865/814098373228625970/tenor_2.gif']
            embed.set_image(url=(random.choice(hugs)))
            await ctx.send(embed=embed)

    @commands.command()
    async def slap(self, ctx: Context, member: typing.Optional[discord.Member]):
        """Slap your archnemesis...or make Cloudy slap you
        
        Parameters
        -----------
        member: discord.Member, optional
            the person to slap
        """
        author = ctx.message.author.mention
        if member == None:
            await ctx.reply(f"Cloudy slapped {author}! sorry!!!!")
        else:
            embed = discord.Embed(description=f'{author} slapped {member.name}!', color=0x2a3387)
            embed.set_image(url='https://cdn.discordapp.com/attachments/804482120671821865/814100958463524884/nK.gif')
            await ctx.send(embed=embed)
    
    @commands.command()
    async def ship(self, ctx: Context, *, ship: str):
        """Cloudy will tell you whether they love your favorite ship or not
        
        Parameters
        -----------
        ship: str
            the shipname/people you ship
        """
        choices = ["I ship", "I don't ship"]
        message = await ctx.send("{} {}!" .format(random.choice(choices), ship))
        if "don't" in message.content:
            await message.add_reaction('💔')
        else:
            await message.add_reaction('💞')

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def dm(self, ctx: Context, member: typing.Optional[discord.Member], *, message: str):
        """Send a DM to someone via Cloudy, or get Cloudy to DM you
        
        Parameters
        -----------
        member: discord.Member, optional
            who you want to message
        message: str
            the message you want to send
        """
        try:
            if member == None:
                ctx.author.send(message)
            else:
                await member.send(f'{message}\n``sent from {ctx.author.display_name}``')
            message = ctx.message
            await message.add_reaction('💌')
        except discord.errors.Forbidden():
            await ctx.reply("I can't dm this user!")

    @commands.command()
    async def embed(self, ctx: Context, *, message:str):
        """Cloudy sends your message, but in an embed
        
        Parameters
        -----------
        message: str
            the message to embed
        """
        colors = [0x99e9ff, 0xac58ed, 0xff7ab6, 0x7cf7a3, 0xf1ff94, 0x978aff]
        randomcolor = random.choice(colors) 
        embed = discord.Embed(title=f'{message}', colour=randomcolor)
        embed.set_footer(text=f'-{ctx.author}', icon_url=ctx.message.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def greet(self, ctx: Context):
        """Greet Cloudy and Cloudy will greet you back"""
        await ctx.reply("Say hello!")

        def check(m):
            return m.content == "hello"

        msg = await self.bot.wait_for("message", check=check)
        await ctx.reply(f"Hello {msg.author}!")

    @commands.command()
    async def number(self, ctx: Context):
        """Sends you a random number within your given range"""
        await ctx.reply('What do you want your lowest possible number to be?')
        number1 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        number1 = int(number1.content)
        await ctx.reply('OK, noted! What do you want the highest number to be?')
        number2 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        number2 = int(number2.content)
        await ctx.reply(random.randrange(number1, number2))

    @commands.command()
    async def choose(self, ctx: Context, *choices: str):
        """Hard to choose what you want for dinner? Cloudy will make a choice for you!
        
        Parameters
        -----------
        choices: str
            the options to choose from
        """
        await ctx.reply(random.choice(choices))

    @commands.command(name='8ball', aliases=["8b", "b"])
    async def ball(self, ctx: Context, *, question: str):
        """Tells you your faith or gives you advice, like all magic 8 balls do.
        
        Parameters
        -----------
        question: str
            the question you need answered
        """
        message = ctx.message
        options = ['It is certain.', 'It is decidedly so.', 'Without a doubt.', 'Yes, definitely.', 'You may rely on it.', 'As I see it, yes.', 'Most likely.', 'Outlook good.', 'Yes.', 'Signs point to yes.', 'Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.', 'Cannot predict now.', 'Concentrate and ask again.', "Don't count on it.", 'My reply is no.', 'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
        async with ctx.typing():
            await asyncio.sleep(2)
        await message.add_reaction('🎱')
        await asyncio.sleep(0.7)
        await ctx.reply(f'**"{question}"**\n' + random.choice(options))

    @commands.command(name='imgur', pass_context=True)
    async def imgur(self, ctx: Context, *text: str):
        """Will search Imgur and return an image
        
        Parameters
        -----------
        text: str
            what to search imgur for
        """
        rand = random.randint(0, 29)
        try:
            if text == ():
                await ctx.send('Remember to put what you want to search for!')
            elif text[0] != ():
                items = imgur.gallery_search(" ".join(text[0:len(text)]), advanced=None, sort='viral', window='all',page=0)
                await ctx.send(items[rand].link)

        except IndexError:
                await ctx.reply("Sorry, I couldn't find a photo of that on imgur!")
                
    
    @commands.group(invoke_without_command=True)
    async def gif(self, ctx: Context, *, searchterm: typing.Optional[str] = None):

        """Searches for a GIF on Giphy
        
        Parameters
        -----------
        searchterm: str, optional
            what you want to search for on giphy
        """

        try:

            if searchterm == None:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.giphy.com/v1/gifs/trending?api_key={giphy_api}&limit=25&rating=g") as api:
                        json = await api.json()
                        elements = json["data"]
                        results = elements[random.choice(range(0, 24))]
                        embed = await gif_embed(results, searchterm)
                        await ctx.send(embed=embed)
            # if there is a search term it fetches the api for the search term specified
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.giphy.com/v1/gifs/search?api_key={giphy_api}&q={searchterm}&limit=25&offset=0&rating=g&lang=en") as api:
                        json = await api.json()
                        elements = json["data"]
                        results = elements[random.choice(range(0, 24))]
                        embed = await gif_embed(results, searchterm)
                        await ctx.send(embed=embed)

        except IndexError:
            await ctx.reply("Sorry, I couldn't find enough GIFs. You can try `gif lite` or `gif mini` in order to fetch less GIFs with a bigger chance of finding a GIF!")

    @gif.command()
    async def lite(self, ctx: Context, *, searchterm: str):

        """Searches for GIFs on Giphy while fetching less GIFs than the regular command
        
        Parameters
        -----------
        searchterm: str
            what you want to search for on giphy
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.giphy.com/v1/gifs/search?api_key={giphy_api}&q={searchterm}&limit=25&offset=0&rating=g&lang=en") as api:
                json = await api.json()
                elements = json["data"]
                results = elements[random.choice(range(0, 12))]
                embed = await gif_embed(results, searchterm)
                await ctx.send(embed=embed)

    @gif.command()
    async def mini(self, ctx: Context, *, searchterm: str):

        """Searches for GIFs on Giphy while fetching less GIFs than the regular and lite commands
        
        Parameters
        -----------
        searchterm: str
            what you want to search for on giphy
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.giphy.com/v1/gifs/search?api_key={giphy_api}&q={searchterm}&limit=25&offset=0&rating=g&lang=en") as api:
                json = await api.json()
                elements = json["data"]
                results = elements[random.choice(range(0, 3))]
                embed = await gif_embed(results, searchterm)
                await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def clock(self, ctx: Context, *, place: str):
        """Returns the current time in the specified area
        
        Parameters
        -----------
        place: str
            the area you want to know the time for
        """
        try:
            text = place.replace(" ", "_")
            country_time_zone = pytz.timezone(text)
            country_time = datetime.datetime.now(country_time_zone)
            place1, place2 = place.split("/")
            place = place2.title()
            embed = discord.Embed(title=f"Current date & time | {place1.title()}", description=(country_time.strftime(f"In {place} it is currently %I:%M %p (%B %d)")), color=discord.Colour.random())
            await ctx.reply(embed=embed)
        except pytz.UnknownTimeZoneError:
            await ctx.send("That timezone isn't formatted correctly/doesn't exist in the tz database. Make sure you use the following format: `Area/City`. To get a list of all the areas: `+clock areas`")

    @clock.command()
    async def areas(self, ctx: Context):
        """Returns a list of valid areas to use with the clock command"""
        embed = discord.Embed(title="List of valid Areas", description="• Africa\n• America\n• Antarctica\n• Arctic\n• Asia\n• Atlantic\n• Australia\n• Europe\n• Indian\n• Pacific", color=discord.Colour.random())
        await ctx.send(embed=embed)

    @commands.command(help="Sends a cat photo")
    async def cat(self, ctx: Context):
        async with self.bot.session.get("https://api.thecatapi.com/v1/images/search") as api:
            json = await api.json()
            elements = json[0]
            await ctx.send(elements["url"])

    @commands.command(help="Sends a dog photo")
    async def dog(self, ctx: Context):
        async with self.bot.session.get("https://dog.ceo/api/breeds/image/random") as api:
            json = await api.json()
            await ctx.send(json['message'])

    @commands.command()
    async def lyrics(self, ctx: Context, *, song_name: Optional[str]):
        """Gets song lyrics
        
        Parameters
        -----------
        song_name: str, optional
            the name of the song to get the lyrics to
        """
        mimx = LyricsFinder()
        if not song_name:
            spotify = discord.utils.find(lambda a: isinstance(a, discord.Spotify), ctx.author.activities)
            if spotify:
                song_name = f"{spotify.title} {spotify.artist}"
            else:
                return await ctx.reply("I need the name of a song to look for lyrics!")
        new_song_name = song_name.replace(' ', '-')
        songs = await mimx.song_search(new_song_name)
        try:
            if len(songs) == 0:
                await ctx.reply("Couldn't find that song!")
            else:
                track: Track = songs[0]
                lyrics = await track.get_lyrics()
                embed = discord.Embed(title=track.name, description=lyrics)
                embed.set_thumbnail(url=track.cover_art)
                await ctx.reply(embed=embed, view=SpotifyView("https://open.spotify.com/track/" + track.spotify_id))
        except:
            await ctx.reply(f"Looks like I couldn't find lyrics for **{song_name}**")

    @commands.command(aliases=['affirmation'])
    async def affirmate(self, ctx: Context):
        """Sends affirmations"""
        async with self.bot.session.get("https://www.affirmations.dev/") as api:
            json = await api.json()
            await ctx.reply(json['affirmation'])

async def setup(bot):
    await bot.add_cog(Fun(bot))