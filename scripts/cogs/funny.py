import discord
from discord.ext import commands



class funny_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.counter = 0


    @discord.ui.button(label="green", style=discord.ButtonStyle.green)
    async def green(self, interaction, button):
        self.counter += 1
        self.green.disabled = True
        self.red.disabled = False
        await interaction.response.edit_message(content=f"funny button {self.counter}", view=self)


    @discord.ui.button(label="red", style=discord.ButtonStyle.red)
    async def red(self, interaction, button):
        self.counter += 1
        self.green.disabled = False
        self.red.disabled = True
        await interaction.response.edit_message(content=f"funny button {self.counter}", view=self)





class Funny(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def funny(self, ctx):
        if ctx.author.bot:
            return

        await ctx.send("funny button", view=funny_button())




async def setup(bot):
    await bot.add_cog(Funny(bot))
