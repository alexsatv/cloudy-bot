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
from discord import app_commands
import traceback
from setup.config import *
from typing import Optional
from io import BytesIO
import sys

# Modals

class RecruitModal(discord.ui.Modal, title="Chroma Recruit"):
	instagram = discord.ui.TextInput(label="Instagram Username", placeholder="Put username here...")
	edit_link = discord.ui.TextInput(label="Link to edit (Instagram/Streamble/TikTok)", placeholder="Put a link to an edit here...")
	program = discord.ui.TextInput(label="Editing Program", placeholder="Put the editing program you use here...")
	other = discord.ui.TextInput(label="Anything else you want us to know?", placeholder="Put other information here...", required=False)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer()
		embed = discord.Embed(title="Chroma 2023 Recruit 🌈", description="", color=0x303136)
		embed.add_field(name="Discord ID", value=interaction.user.id, inline=False)
		embed.add_field(name="Instagram Username", value=self.instagram.value, inline=False)
		embed.add_field(name="Account Link", value=f"https://instagram.com/{self.instagram.value}")
		embed.add_field(name="Edit Link", value=self.edit_link.value, inline=False)
		embed.add_field(name="Editing Program", value=self.program.value, inline=False)
		embed.set_thumbnail(url="https://rqinflow.com/static/chroma-pfp-animation.gif")
		if self.other.value:
			embed.add_field(name="Anything else", value=self.other.value, inline=False)
		async with interaction.client.db.cursor() as cursor:
			try:
				await cursor.execute('''INSERT INTO applications (user_id, instagram, accepted, apply_number) VALUES (?, ?, ?, ?)''', (interaction.user.id, self.instagram.value, 0, 1))
				await interaction.client.db.commit()
			except Exception as e:
				if str(e) == "UNIQUE constraint failed: applications.instagram" or str(e) == "UNIQUE constraint failed: applications.user_id":
					await cursor.execute('''UPDATE applications SET apply_number = ? WHERE user_id = ?''', (2, interaction.user.id))
					await interaction.client.db.commit()
					#return await interaction.followup.send(f"An entry for **{self.instagram.value}** has already been registered. If this wasn't you, please notify a staff member and they will help you out!", ephemeral=True)
				else:
					traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
					return await interaction.followup.send("Something went wrong!", ephemeral=True)
			msg = await interaction.client.get_channel(835497793703247903).send(embed=embed)
			await cursor.execute('''UPDATE applications SET msg_id = ? WHERE user_id = ?''', (msg.id, interaction.user.id))
			await interaction.client.db.commit()
		await interaction.followup.send(f'Thanks for joining the recruit!', ephemeral=True)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
		traceback.print_tb(error.__traceback__)
		
class StaffApps(discord.ui.Modal, title="Chroma Staff Application - Helper"):
	user = discord.ui.TextInput(label="What's your username?", placeholder="Put your Instagram @ here...", style=discord.TextStyle.short)
	why = discord.ui.TextInput(label="Why should we pick you?", placeholder="Put your reasoning here...", style=discord.TextStyle.paragraph)
	experience = discord.ui.TextInput(label="What kind of previous experience do you have?", placeholder="List your previous experience here...", style=discord.TextStyle.paragraph)
	events = discord.ui.TextInput(label="What would you contribute with?", placeholder="E.g. Events you wanna host and why, things you wanna improve in Chroma etc...", style=discord.TextStyle.paragraph)
	other = discord.ui.TextInput(label="Anything else you want us to know?", placeholder="Extra information goes here...", style=discord.TextStyle.paragraph, required=False)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer()
		for response in [self.why.value, self.experience.value, self.events.value, self.other.value]:
			if response is not None:
				if len(response) > 1024:
					return await interaction.followup.send("Your form reply exceeds our limits, try shortening your responses!", ephemeral=True)
		embed = discord.Embed(title="General Staff Application 🌈", description="", color=0x2B2D31)
		embed.add_field(name="Instagram Username", value=self.user.value, inline=False)
		embed.add_field(name="Why should we pick you?", value=self.why.value)
		embed.add_field(name="What kind of previous experience do you have?", value=self.experience.value, inline=False)
		embed.add_field(name="What kind of activities and/or events would you initiate in Chroma?", value=self.events.value, inline=False)
		embed.set_thumbnail(url="https://rqinflow.com/static/chroma-pfp-animation.gif")
		if self.other.value:
			embed.add_field(name="Anything else you want us to know?", value=self.other.value, inline=False)
		async with interaction.client.db.cursor() as cursor:
			try:
				await cursor.execute('''INSERT INTO staff_apps (user_id, instagram) VALUES (?, ?)''', (interaction.user.id, self.user.value))
				await interaction.client.db.commit()
			except Exception as e:
				if str(e) == "UNIQUE constraint failed: staff_apps.instagram":
					return await interaction.followup.send(f"An application for **{self.instagram.value}** has already been filled out.", ephemeral=True)
				else:
					print(str(e))
					return await interaction.followup.send("Something went wrong!", ephemeral=True)
			msg = await interaction.client.get_channel(1098242178947481741).send(embed=embed, content=f"ID: {interaction.user.id}")
			await cursor.execute('''UPDATE staff_apps SET msg_id = ? WHERE user_id = ?''', (msg.id, interaction.user.id))
			await interaction.client.db.commit()
		await interaction.followup.send(f'Thanks for applying to be a part of the Chroma staff! We appreciate it <3', ephemeral=True)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
		traceback.print_tb(error.__traceback__)

class GfxApps(discord.ui.Modal, title="Chroma Staff Application - GFX"):

	def __init__(self, files: list = None):
		super().__init__()
		self.files = files

	user = discord.ui.TextInput(label="What's your username?", style=discord.TextStyle.short)
	why = discord.ui.TextInput(label="Why do you want to be a part of our staff?", style=discord.TextStyle.paragraph)
	time = discord.ui.TextInput(label="How quickly can you usually make GFX?", default="Instagram thumbnails:\nDiscord server banners:\nRecruit videos:", style=discord.TextStyle.paragraph)
	other = discord.ui.TextInput(label="Anything else you want us to know?", style=discord.TextStyle.paragraph, required=False)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer()
		for response in [self.why.value, self.time.value, self.other.value]:
			if response is not None:
				if len(response) > 1024:
					return await interaction.followup.send("Your form reply exceeds our limits, try shortening your responses!", ephemeral=True)
		embed = discord.Embed(title="GFX Application 🌈", description="", color=0x2B2D31)
		embed.add_field(name="Instagram Username", value=self.user.value, inline=False)
		embed.add_field(name="Why do you want to be a part of our staff?", value=self.why.value)
		embed.add_field(name="How quickly can you make GFX (e.g. thumbnails, banners)?", value=self.time.value, inline=False)
		embed.set_thumbnail(url="https://rqinflow.com/static/chroma-pfp-animation.gif")
		if self.other.value:
			embed.add_field(name="Anything else you want us to know?", value=self.other.value, inline=False)
		if self.files != None:
			await interaction.client.get_channel(1098242178947481741).send(embed=embed, content=f"ID: {interaction.user.id}")
			await interaction.client.get_channel(1098242178947481741).send(content=f"{interaction.user.mention}'s previous work", files=self.files)
		else:
			await interaction.client.get_channel(1098242178947481741).send(embed=embed)
		await interaction.followup.send(f'Thanks for applying to be a part of the Chroma staff! We appreciate it <3', ephemeral=True)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
		traceback.print_tb(error.__traceback__)

# Cog for slash commands

class Slash(commands.Cog):
	"""All of cloudy's slash commands"""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot: commands.Bot = bot
		super().__init__()

	@app_commands.command(description="Join the Chroma Recruit")
	async def apply(self, interaction: discord.Interaction):
		async with interaction.client.db.cursor() as cursor:
			await cursor.execute('''SELECT * FROM applications WHERE user_id = ?''', (interaction.user.id,))
			row = await cursor.fetchone()
			if row is not None:
				if int(row[4]) == 2:
					return await interaction.response.send_message("You've already applied twice!", ephemeral=True)
		await interaction.response.send_modal(RecruitModal())
		
	@app_commands.command(description="Check how many times you've applied")
	async def applycheck(self, interaction: discord.Interaction):
		await interaction.response.defer(ephemeral=True)
		async with interaction.client.db.cursor() as cursor:
			await cursor.execute('''SELECT * FROM applications WHERE user_id = ?''', (interaction.user.id,))
			row = await cursor.fetchone()
			if row is not None:
				if int(row[4]) == 2:
					times = 2
				if int(row[4]) == 1:
					times = 1
			else:
				times = 0
		await interaction.followup.send(f"You have applied {times} time!" if times == 1 else f"You have applied {times} times!", ephemeral=True)
		
	@app_commands.command(description="Get our logos")
	@app_commands.guilds(discord.Object(id=694010548605550675))
	async def logos(self, interaction: discord.Interaction):
		"""Get our logos"""
		await interaction.response.defer(ephemeral=True)
		channel = self.bot.get_channel(1069358104740900985)
		await channel.send(f"{interaction.user.mention} used the `logos` command!")
		await interaction.followup.send(content=f"key: `{logo_code}`\n{logos}", ephemeral=True)

	@app_commands.command(description="Apply to be a part of the Chroma staff")
	@app_commands.guilds(discord.Object(id=694010548605550675))
	async def staff(self, interaction: discord.Interaction):
		async with interaction.client.db.cursor() as cursor:
			await cursor.execute('''SELECT * FROM staff_apps WHERE user_id = ?''', (interaction.user.id,))
			row = await cursor.fetchone()
			if row:
				return await interaction.response.send_message('You have already applied for staff!', ephemeral=True)
		await interaction.response.send_modal(StaffApps())

	@app_commands.command(description="Apply to be a Chroma GFX designer")
	@app_commands.guilds(discord.Object(id=694010548605550675))
	async def gfx(self, interaction: discord.Interaction, artwork: Optional[discord.Attachment], artwork2: Optional[discord.Attachment], artwork3: Optional[discord.Attachment], artwork4: Optional[discord.Attachment]):
		files = []
		for attachment in [artwork, artwork2, artwork3, artwork4]:
			if attachment and attachment.size > 0:
				fil = discord.File(BytesIO(await attachment.read()), filename=attachment.filename)
				files.append(fil)
		if len(files) > 0:
			await interaction.response.send_modal(GfxApps(files))
		else:
			await interaction.response.send_modal(GfxApps())

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Slash(bot))
