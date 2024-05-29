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
import datetime
import platform
import time
from typing import Optional
import humanize
import asyncpg
from utils.subclasses import Context

class Misc(commands.Cog, name="Misc"):
    """Miscellaneous commands"""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def can_close():
        async def predicate(ctx):
            role_id = 835549528932220938
            role = ctx.guild.get_role(role_id)
            return role in ctx.author.roles or ctx.author.id == ctx.channel.owner_id
        return commands.check(predicate)
    
    def get_color(self, status: str) -> int:
        if "dnd" in status:
            color = 0xfa002e
        elif "online" in status:
            color = 0x2afa00
        elif "idle" in status:
            color = 0xfaaf00
        return color

    def get_badges(self, member: discord.Member, user: discord.User, flags: str, badgeslist: list) -> None:
        if "hypesquad_balance" in str(flags):
            badgeslist.append("<:balance_icon:937770399880585287> HypeSquad Balance")
        elif "hypesquad_bravery" in str(flags):
            badgeslist.append("<:bravery_icon:937767201094631444> HypeSquad Bravery")
        elif "hypesquad_brilliance" in str(flags):
            badgeslist.append("<:brilliance_icon:937770447838281758> HypeSquad Brilliance")
        if "active_developer" in str(flags):
            badgeslist.append("<:active_dev:1078684899172692020> Active Developer")
        if member.avatar.is_animated():
            badgeslist.append("<:nitro_icon:937770475625525289> Nitro")
        elif member.discriminator == "0001":
            badgeslist.append("<:nitro_icon:937770475625525289> Nitro")
        elif member.premium_since is not None:
            badgeslist.append("<:nitro_icon:937770475625525289> Nitro")
        elif user.banner is not None:
            badgeslist.append("<:nitro_icon:937770475625525289> Nitro")
        if member.premium_since is not None:
            badgeslist.append("<a:boost:938021210984419338> Booster")

    async def get_user_data(self, userid: int) -> asyncpg.Record:
        query = "SELECT * FROM user_info WHERE user_id = $1;"
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                info = await connection.fetchrow(query, userid)
        await self.bot.pool.release(connection)
        return info
    
    async def set_afk(self, userid: int, reason: str) -> None:
        query = "INSERT INTO afk (user_id, reason, time) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO UPDATE SET reason = $2, time = $3"
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(query, userid, reason, discord.utils.utcnow())
        await self.bot.pool.release(connection)

    @commands.command()
    @can_close()
    async def solved(self, ctx: Context):
        """Marks a form post as solved and archives it"""
        assert isinstance(ctx.channel, discord.Thread)
        await ctx.message.add_reaction("✅")
        tag = discord.utils.get(ctx.channel.parent.available_tags, name="Solved")
        tags = ctx.channel.applied_tags
        new_tags = [tag]
        for t in tags:
            new_tags.append(t)
        await ctx.channel.edit(locked=True, archived=True, applied_tags=new_tags, reason=f'Marked as solved by {ctx.author} (ID: {ctx.author.id})')

    @commands.command(aliases=["about"])
    async def botinfo(self, ctx: Context):
        """Sends info about the bot"""
        delta_uptime = datetime.datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        embed = discord.Embed(title="About Cloudy", description=f"Cloudy is a multi-purpose bot made for [Chroma](https://instagram.com/chromagrp)\nFor help regarding commands do `+help`\n\n**<a:cake:1070076628857782363> Date of birth:** {discord.utils.format_dt(self.bot.user.created_at, 'D')}\n\n**<:update:1070078013909237810> Last reboot**: {discord.utils.format_dt(self.bot.launch_time, 'D')}\n\n**<:upvote:1007251428324151366> Uptime: **{days} days and {hours} hours\n\n**👥 Total users:** {sum(g.member_count for g in self.bot.guilds)}\n\n**<:python:1070074577666973706> Python version:** {platform.python_version()}\n\n**<:dpy:1070074928797339701> Discord.py version:** {discord.__version__}\n\n**<:msg:1070088880264597556> Typing latency:** Loading...\n\n**<:ws:1070085077276569750> Websocket latency:** {round(self.bot.latency * 1000)}ms")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Made with 💌 by {self.bot.application.owner.name}#{self.bot.application.owner.discriminator}")
        start = time.perf_counter()
        message = await ctx.send(embed=embed)
        end = time.perf_counter()
        duration = (end - start) * 1000
        embed.description = f"Cloudy is a multi-purpose bot made for [Chroma](https://instagram.com/chromagrp)\nFor help regarding commands do `+help`\n\n**<a:cake:1070076628857782363> Date of birth:** {discord.utils.format_dt(self.bot.user.created_at, 'D')}\n\n**<:update:1070078013909237810> Last reboot**: {discord.utils.format_dt(self.bot.launch_time, 'D')}\n\n**<:upvote:1007251428324151366> Uptime: **{days} days and {hours} hours\n\n**👥 Total users:** {sum(g.member_count for g in self.bot.guilds)}\n\n**<:python:1070074577666973706> Python version:** {platform.python_version()}\n\n**<:dpy:1070074928797339701> Discord.py version:** {discord.__version__}\n\n**<:msg:1070088880264597556> Typing latency:** {int(duration)}ms\n\n**<:ws:1070085077276569750> Websocket latency:** {round(self.bot.latency * 1000)}ms"
        await message.edit(embed = embed)

    @commands.command()
    async def device(self, ctx: Context, member: Optional[discord.Member]):
        """Check what device(s) is currently being used

        Parameters
        -----------
        member: discord.Member, optional
            the person to check
        """
        if not member:
            member = ctx.author
        devices = {}
        actives = {"mobile": 0, "desktop": 0, "web": 0}
        if "offline" not in member.mobile_status:
            actives["mobile"] = 1
            devices["mobile"] = member.mobile_status
        if "offline" not in member.desktop_status:
            actives["desktop"] = 1
            devices["desktop"] = member.desktop_status
        if "offline" not in member.web_status:
            actives["web"] = 1
            devices["web"] = member.web_status
        embed = discord.Embed()
        embed.set_author(name="Activity status", icon_url=member.display_avatar.url)
        if len(devices) == 1:
            for key in actives:
                if actives[key] == 1:
                    current = key
            embed.description = f"{member.name} is currently using a {current} device"
            embed.color = self.get_color(devices[current])
        if len(devices) == 0:
            embed.description = f"{member.name} is currently offline on all devices"
            embed.color = 0x969696
        if len(devices) == 2:
            active_devs = []
            for key in actives:
                if actives[key] == 1:
                    active_devs.append(key)
            current = (" device and a ").join(active_devs)
            embed.description = f"{member.name} is currently using a {current} device."
            embed.color = self.get_color(devices[active_devs[0]])
        if len(devices) == 3:
            active_devs = []
            for key in actives:
                if actives[key] == 1:
                    active_devs.append(key)
            current = (" device, a ").join(active_devs)
            embed.description = f"{member.name} is currently using a {current} device."
            embed.color = self.get_color(devices[active_devs[0]])
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx: Context):
        """Ping-pong! Sends latency"""
        embed = discord.Embed(title="🏓 Pong!")
        start = time.perf_counter()
        message = await ctx.send(embed=embed)
        end = time.perf_counter()
        duration = (end - start) * 1000
        embed.add_field(name="Websocket latency", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        embed.add_field(name="Typing latency", value=f"{int(duration)}ms", inline=False)
        await message.edit(embed=embed)

    @commands.command(help="Sends info about a user", aliases=['ui'])
    async def userinfo(self, ctx: Context, member: Optional[discord.Member]=None):
        """Get info about a discord user
        
        Parameters
        -----------
        member: discord.Member, optional
            the user to get info on
        """
        if member == None:
            member = ctx.author
        createdat = member.created_at
        joinedat = member.joined_at
        created = time.mktime(createdat.timetuple())
        joined = time.mktime(joinedat.timetuple())
        flags = member.public_flags.all()
        badgeslist = []
        user = await self.bot.fetch_user(member.id)
        self.get_badges(member, user, flags, badgeslist)
        badges = ' \n'.join([str(elem) for elem in badgeslist])
        embed = discord.Embed(title=member.name)
        if user.banner is not None:
            embed.set_image(url=user.banner)
        embed.set_thumbnail(url=member.avatar.url)
        data = await self.get_user_data(member.id)
        try:
            if data['last_seen'] == None:
                await embed.add_field(name="<:status_online:998595341450481714> Activity", value=f'Active for **{humanize.precisedelta(discord.utils.utcnow() - data["online_since"], minimum_unit="seconds", format="%0.0f")}**')
            else:
                await embed.add_field(name="<:status_offline:998595266062061653> Activity", value=f'Went offline {discord.utils.format_dt(data["last_seen"], "R")}')
        except Exception as error:
            if str(error) == "'NoneType' object is not subscriptable":
                return
            else:
                print(error)
        embed.add_field(name="<:name:938019997656174622> Nickname", value=member.nick, inline=False)
        embed.add_field(name="<:magicwand:938019572165009448> Created at", value=f"<t:{int(created)}:D> (<t:{int(created)}:R>)", inline=False)
        embed.add_field(name="<:green_arrow:937770497557553222> Joined", value=f"<t:{int(joined)}:D> (<t:{int(joined)}:R>)", inline=False)
        if len(badgeslist) > 0:
            embed.add_field(name="<a:badges:938023584142622791> Badges", value=f"{badges}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['act'])
    async def activity(self, ctx: Context, member: Optional[discord.Member]=None):
        """Sends activity status
        
        Parameters
        -----------
        member: discord.Member, optional
            the member to get activity status for
        """
        if not member:
            member = ctx.author
        data = await self.get_user_data(member.id)
        embed = discord.Embed(title="Activity")
        try:
            if data['last_seen'] == None:
                embed.description = f'{member.display_name} has been active for **{humanize.precisedelta(discord.utils.utcnow() - data["online_since"], minimum_unit="seconds", format="%0.0f")}**'
            else:
                embed.description = f'{member.display_name} went offline {discord.utils.format_dt(data["last_seen"], "R")}'
            await ctx.reply(embed=embed)
        except Exception as error:
            if str(error) == "'NoneType' object is not subscriptable":
                await ctx.send("I don't have activity data on this user!")

    @commands.command()
    async def source(self, ctx: Context):
        """Get cloudy's source code"""
        await ctx.send("https://github.com/rqinflow/cloudy-bot")

    @commands.command()
    async def afk(self, ctx: Context, *, reason: str):
        """Set an afk reason when you go afk
        
        Parameters
        -----------
        reason: str
            the reason why you're going to be afk
        """
        await self.set_afk(ctx.author.id, reason)
        await ctx.reply(f"✅ Successfully set your afk reason to *{reason}*!")

    @commands.command()
    async def serverinfo(self, ctx):
        embed = discord.Embed(title="SERVER INFO", description=f"Name: **{ctx.guild.name}**\n<:1166196254141861979:1244752051313840199>ID: **1121841073673736215**\n<:1166196254141861979:1244752051313840199>Owned by: **<@{ctx.guild.owner_id}>**\n<:1166196258499727480:1244752002492268685>Date created: <t:1585600920:D>\n<:CF10:1244752150613987460>**{len(ctx.guild.channels)}** channels\n<:CF10:1244752150613987460>**{len(ctx.guild.roles)}** roles\n<:CF10:1244752150613987460>**{ctx.guild._member_count}** members\n<:CF10:1244752150613987460>**{ctx.guild.premium_subscription_count}** boosts\n<:Empty:1244752102807441540><:1166196254141861979:1244752051313840199>Booster tier: **{ctx.guild.premium_tier}**\n<:Empty:1244752102807441540><:1166196258499727480:1244752002492268685>Booster role: <@&{ctx.guild.premium_subscriber_role.id}>", color=0x2b2d31)
        embed.set_thumbnail(url=ctx.guild.icon)
        embed.set_image(url=ctx.guild.banner)
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Misc(bot))