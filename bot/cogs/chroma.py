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
from io import BytesIO
import ftplib
from setup.config import *
from urllib.parse import quote_plus
from utils.subclasses import Context
from typing import Optional
import asyncpg

class infoview(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(label="Logos")
    async def klogos(self, interaction: discord.Interaction, button: discord.ui.Button):
        logosembed = discord.Embed(title="<a:bun:1098764398962671677> Chroma Logos!", description="˃ Please make sure you watermark the logos!\n˃ Use the hashtag on every edit\n˃ Do not share this link with anyone outside the group!", color=0x2b2d31)
        logosembed.set_footer(text="Made us some logos? send them to Reece or Alisha!")
        logosembed.set_image(url=interaction.guild.banner)
        await interaction.user.send(f"key: `{logo_code}`\n{logos}\nhashtag: #𝗰𝗵𝗿𝗼𝗺𝗮𝗴𝗿𝗽", embed=logosembed)
        channel = interaction.client.get_channel(1069358104740900985)
        log = discord.Embed(title="Logo button has been used!", description=f"`{interaction.user.display_name}` has used the logos button", color=0x2b2d31)
        log.set_footer(text=f"id: {interaction.user.id}", icon_url=interaction.user.display_avatar)
        await channel.send(embed=log)
        await interaction.response.send_message(f'I have sent you the logos! Check your DMs', ephemeral=True)

class DownloadView(discord.ui.View):
    def __init__(self, username: str):
        super().__init__()

        username = quote_plus(username)
        self.add_item(discord.ui.Button(label='Download', url=f'https://cdn.rqinflow.com/files/{username}.mp4'))

class Chroma(commands.Cog, name="Chroma", description="Includes the commands associated with [Chroma group](https://www.instagram.com/chromagrp) and its members!"):
    def __init__(self, bot):
        self.bot = bot

    """ def cog_unload(self) -> None:
        firebase_admin.delete_app(secondaryApp) """
    
    async def add_username(self, username: str) -> bool:
        query = "INSERT INTO edits (username) VALUES ($1)"
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    await connection.execute(query, username)
                except asyncpg.exceptions.UniqueViolationError:
                    pass
        await self.bot.pool.release(connection)

    async def get_edit(self) -> str:
        query = "SELECT username from edits"
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                    data = await connection.fetch(query)
        await self.bot.pool.release(connection)
        choice = random.choice(data)
        return choice["username"]
    
    @commands.command(aliases=["edit"])
    async def edits(self, ctx: Context):
        """Sends an edit made by a Chroma member"""
        edit = await self.get_edit()
        await ctx.send("https://cloudy.rqinflow.com/" + edit, view=DownloadView(edit))

    @commands.command(aliases=["upl"], hidden=True)
    async def upload(self, ctx: Context, username: str):
        """Adds edit to edits command

        Parameters
        -----------
        username: str
            your instagram username
        """
        stored_guild_id = 694010548605550675
        if ctx.guild.id == stored_guild_id:
            if ctx.message.attachments:
                f = ctx.message.attachments[0]
                myfile = BytesIO(await f.read())
                myfile.seek(0)
                new_username = username + ".mp4"
                if f.content_type == "video/mp4" or f.content_type == "video/quicktime":
                    session = ftplib.FTP(ftp_host,ftp_username,ftp_password)
                    session.storbinary(f'STOR {new_username}', myfile)
                    session.close()
                    await self.add_username(username=username)
                    await ctx.send(f"Succesfully uploaded the edit!")
                    await ctx.send(f"https://cloudy.rqinflow.com/{username}")
                else:
                    await ctx.send(f"Your file is in the {f.content_type} format, and it needs to be video/mp4 or video/quicktime")
            else:
                await ctx.send("Please provide an attachment of your edit along with your username!")
        else:
            await ctx.send("This command can only be used in the private Chroma server.")

    @commands.command()
    async def hi(self, ctx: Context):
        """Cloudy says hi :)"""
        name = ctx.message.author.mention
        await ctx.send(f'hi {name}! i hope ur having a great day ily<3')

    @commands.command()
    async def memberinfo(self, ctx: Context, user: Optional[discord.Member] = None):
        """Sends info about a member
        
        Parameters
        -----------
        user: discord.Member, optional
            the user to get info on
        """
        stored_guild_id = 694010548605550675
        if user == None:
            user = ctx.author
        display = user.display_name
        sheher = discord.utils.find(lambda r: r.name == 'she/her', ctx.message.guild.roles)
        theythem = discord.utils.find(lambda r: r.name == 'they/them', ctx.message.guild.roles)
        shethey = discord.utils.find(lambda r: r.name == 'she/they', ctx.message.guild.roles)
        hethey = discord.utils.find(lambda r: r.name == 'he/they', ctx.message.guild.roles)
        hehim = discord.utils.find(lambda r: r.name == 'he/him', ctx.message.guild.roles)
        any = discord.utils.find(lambda r: r.name == 'any pronouns', ctx.message.guild.roles)
        role1 = discord.utils.find(lambda r: r.name == 'after effects', ctx.message.guild.roles)
        role2 = discord.utils.find(lambda r: r.name == 'videostar', ctx.message.guild.roles)
        role3 = discord.utils.find(lambda r: r.name == 'alight motion', ctx.message.guild.roles)
        role4 = discord.utils.find(lambda r: r.name == 'cute cut pro', ctx.message.guild.roles)
        role5 = discord.utils.find(lambda r: r.name == 'sony vegas pro', ctx.message.guild.roles)
        if user is None:
            user = ctx.message.author
        else:
            pass
        if ctx.guild.id == stored_guild_id:
            title1 = f"chroma member | {display}"
        else:
            title1 = f"editing-info about {display}"
        if role1 in user.roles:
            program = "after effects"
            if role2 in user.roles:
                program = "after effects and video star"
            elif role5 in user.roles:
                program = "after effects and sony vegas pro"
            elif role3 in user.roles:
                program = "after effects and alight motion"
        if role1 not in user.roles:
            if role2 in user.roles:
                program = "video star"
                if role3 in user.roles:
                    program = "video star and alight motion"
                    if role4 in user.roles:
                        program = "video star, alight motion and cute cut pro"
            elif role3 in user.roles:
                program = "alight motion"
                if role4 in user.roles:
                    program = "alight motion and cute cut pro"
            elif role4 in user.roles:
                program = "cute cut pro"
            elif role5 in user.roles:
                program = "sony vegas pro"
            else:
                program = "an unspecified editing software"
        embed = discord.Embed(title="chroma member", description=f"{user.display_name} makes their edits using {program}", color=0xFF90FB)
        if sheher in user.roles:
            prns = "she/her"
            prn1 = "she uses"
            prn2 = "her"
        elif hehim in user.roles:
            prns = "he/him"
            prn1 = "he uses"
            prn2 = "his"
        elif shethey in user.roles:
            prns = "she/they"
            prn1 = "they use"
            prn2 = "her"
        elif hethey in user.roles:
            prns = "he/they"
            prn1 = "they use"
            prn = "his"
        elif theythem in user.roles:
            prns = "they/them"
            prn1 = "they use"
            prn2 = "their"
        elif any in user.roles:
            prns = "any pronouns"
            prn1 = "they use"
            prn2 = "their"
        else:
            prns = "not specified"
            prn1 = "they use"
            prn2 = "their"
        embed = discord.Embed(title=title1, 
        description=f"↬ {display}'s prounouns are {prns}\n↬ {prn1} {program} to edit", color=0xFF90FB)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_image(url="https://media.discordapp.net/attachments/804482120671821865/855135807697321994/2021-06-12_18.40.11.png?width=1191&height=670")
        if "|" in display:
            list = display.split("|")
            name1 = list[0]
            name = name1.replace(" ", "")
            username = list[1]
            acc = username.replace(" ", "")
            embed = discord.Embed(title=title1, 
            description=f"↬ {name}'s pronouns are {prns}\n↬ {prn1} {program} to edit\n↬ [click here to go to {prn2} instagram](https://instagram.com/{acc})", color=0xFF90FB)
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_image(url="https://media.discordapp.net/attachments/804482120671821865/855135807697321994/2021-06-12_18.40.11.png?width=1191&height=670")
            await ctx.reply(embed=embed)
            message = await ctx.send(f"react to this message if you want to see one of {name}'s edits!")
            await message.add_reaction("✅")
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["✅"] and reaction.message == message
            confirmation = await self.bot.wait_for("reaction_add", check=check) 
            if confirmation:
                await message.delete()
                await ctx.send(f"https://cloudy.rqinflow.com/{acc}")
        else:
            await ctx.reply(embed=embed)
        
    """    @commands.command(aliases=['profile', 'ig', 'igprofile', 'insta'])
        async def instagram(self, ctx, username):
            L = instaloader.Instaloader()
            async with ctx.typing():
                username=username
                profile = instaloader.Profile.from_username(L.context, username)
                pfpurl=(profile.profile_pic_url)
                followers=(profile.followers)
                name=(profile.full_name)
                following=(profile.followees)
                bio=(profile.biography)
                embed = discord.Embed(description=(f"**[{name}](http://www.instagram.com/{username})**\n\n{bio}\n\n{name} has **{followers}** followers and follows **{following}** accounts"), color=0x2F3136)
                embed.set_thumbnail(url=f"{pfpurl}")
                embed.set_footer(text="Data from Instagram")
            await ctx.send(embed=embed)"""

    @commands.command(hidden=True)
    @commands.has_role("Server Booster")
    async def claimperks(self, ctx: Context):
        """Command for Server Boosters to claim their perks"""
        guild = 694010548605550675
        if ctx.guild.id == guild:
            embed = discord.Embed(title="resources", color=0xDECAB2)
            embed.add_field(name="starrys.aep resources", value=f"[remember to give credit]({starry_resources})", inline=False)
            embed.add_field(name="grandily doodles", value=f"[remember to give credit]({grandily_resources})", inline=False)
            embed.add_field(name="qtplum resources", value=f"[remember to give credit]({qtplum_resources})", inline=False)
            embed.add_field(name="remqsi colorings", value=f"[remember to give credit]({remqsi_resources})", inline=False)
            embed.add_field(name="blqckthorns shakes and colorings", value=f"[remember to give credit]({blqckthorns_resources})", inline=False)
            embed.add_field(name="_raven.mp4 turbs", value=f"[remember to give credit]({ravenmp4_resources})", inline=False)
            await ctx.author.send(embed=embed)
            await ctx.reply("check your dms!")
        else:
            return

    @commands.command(hidden=True)
    async def info1(self, ctx):
        embed = discord.Embed(title="Welcome to Chroma", color=0x2b2d31)
        embed.add_field(name="Group Rules", value="• Must be following [remqsi](https://instagram.com/remqsi), [wqndqs](https://instagram.com/wqndqs) + [chromagrp](https://instagram.com/chromagrp)"
        "\n• Always use our hashtag #𝗰𝗵𝗿𝗼𝗺𝗮𝗴𝗿𝗽"
        "\n• Watermark logos if the background is mostly plain"
        "\n• Never share the logos with anyone outside of Chroma", inline=False)
        embed.add_field(name="Chat Rules", value="• No NSFW content or sexual discussions"
        "\n• No offensive jokes that can make others uncomfortable"
        "\n• Please stay as active as possible"
        '\n• Set your nickname as "name | username"'
        "\n• No impersonating other editors"
        "\n• Be friendly and respect everyone"
        "\n• If you move accounts or leave, please DM [chromagrp](https://instagram.com/chromagrp)"
        "\n• No trash talking of other groups or editors"
        "\n• Respect the server and use channels correctly", inline=False)
        embed.set_thumbnail(url=ctx.guild.icon)
        await ctx.send(embed=embed, view=infoview())

async def setup(bot):
    await bot.add_cog(Chroma(bot))