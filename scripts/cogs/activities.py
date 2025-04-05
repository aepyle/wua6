import discord
from discord.ext import commands
import random
import asyncio

coins = []
problems = []


class MathProblem(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.Cog.listener()
	async def on_message(self, ctx):
		if not ctx.guild:
			return
		if random.randint(0, 666) == 667 and not ctx.author.bot and ctx.channel not in problems:
			await self.init_problem(ctx)



	async def init_problem(self, ctx):
		num1, num2 = (random.randint(2, 10), random.randint(2, 7))
		operation = random.randint(0, 2)

		if operation == 0:
			question = f"What is {num1} + {num2}?"
			answer = num1 + num2
		elif operation == 1:
			question = f"What is {num1} - {num2}?"
			answer = num1 - num2
		else:
			question = f"What is {num1} x {num2}?"
			answer = num1 * num2

		msg = await ctx.channel.send(question)
		problems.append(msg.channel)

		try:
			response = await self.bot.wait_for('message', timeout=7.5, check=lambda x: str(answer) == x.content)
		except asyncio.TimeoutError:
			await msg.edit(content=f"~~{question}~~")
			problems.remove(msg.channel)
			return
		else:
			await ctx.channel.send(f"**{response.author}** got it right!")
			problems.remove(msg.channel)
			return





class Reactions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.Cog.listener()
	async def on_message(self, ctx):
		if not ctx.guild:
			return

		if random.randint(0, 10) == 1 and not ctx.author.bot:
			coins.append(ctx)
			await ctx.add_reaction("🪙")


		elif random.randint(0, 150) == 69:
			# Get all custom guild emotes
			emojis = ctx.guild.emojis

			# If server has no custom emotes, quit
			if len(emojis) == 0:
				return

			# Select emote at random and add to message
			emoji = emojis[random.randint(0, len(emojis) - 1)]
			await ctx.add_reaction(emoji)

		elif random.randint(1, 150) == 69:
			# Send man standing emoji
			await ctx.channel.send('�')



	@commands.guild_only()
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if reaction.message in coins and reaction.emoji == "🪙" and not user.bot:
			coins.remove(reaction.message)
			await reaction.message.channel.send(f"Congratulations, **{user.name}** hit the button first!")
			await reaction.remove(self.bot.user)





async def setup(bot):
	await bot.add_cog(Reactions(bot))
	await bot.add_cog(MathProblem(bot))
