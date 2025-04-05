import discord
from discord.ext import commands
import discord_utils as dcu

ranking = {"rock": "scissors", "paper": "rock", "scissors": "paper"}


class RPS_View(discord.ui.View):
    def __init__(self, player1, player2=None):
        super().__init__(timeout=60.0)
        self.player1 = player1
        self.player2 = player2
        self.message = None

        self.game = {"player1": None, "player2": None}
        

    @discord.ui.button(label="rock", style=discord.ButtonStyle.gray)
    async def rock(self, interaction, button):
        if (interaction.user == self.player1 and self.game["player1"]) or (interaction.user == self.player2 and self.game["player2"]):
            await interaction.response.send_message("You already selected an option", ephemeral=True)
        else:
            if interaction.user == self.player1:
                self.game["player1"] = "rock"
            elif interaction.user == self.player2:
                self.game["player2"] = "rock"
            elif self.player2 is None:
                self.player2 = interaction.user
                self.game["player2"] = "rock"

            if self.game["player1"] is not None and self.game["player2"] is not None:
                await self.shoot(interaction)
            else:
                await interaction.response.defer()


    @discord.ui.button(label="paper", style=discord.ButtonStyle.green)
    async def paper(self, interaction, button):
        if (interaction.user == self.player1 and self.game["player1"]) or (interaction.user == self.player2 and self.game["player2"]):
            await interaction.response.send_message("You already selected an option", ephemeral=True)
        else:
            if interaction.user == self.player1:
                self.game["player1"] = "paper"
            elif interaction.user == self.player2:
                self.game["player2"] = "paper"
            elif self.player2 is None:
                self.player2 = interaction.user
                self.game["player2"] = "paper"

            if self.game["player1"] is not None and self.game["player2"] is not None:
                await self.shoot(interaction)
            else:
                await interaction.response.defer()


    @discord.ui.button(label="scissors", style=discord.ButtonStyle.blurple)
    async def scissors(self, interaction, button):
        if (interaction.user == self.player1 and self.game["player1"]) or (interaction.user == self.player2 and self.game["player2"]):
            await interaction.response.send_message("You already selected an option", ephemeral=True)
        else:
            if interaction.user == self.player1:
                self.game["player1"] = "scissors"
            elif interaction.user == self.player2:
                self.game["player2"] = "scissors"
            elif self.player2 is None:
                self.player2 = interaction.user
                self.game["player2"] = "scissors"

            if self.game["player1"] is not None and self.game["player2"] is not None:
                await self.shoot(interaction)
            else:
                await interaction.response.defer()


    async def on_timeout(self) -> None:
        # if any buttons are still active, disable them and time the game out
        if not all(item.disabled for item in self.children):
            self.rock.disabled = True
            self.paper.disabled = True
            self.scissors.disabled = True

            await self.message.edit(content="This game has timed out", view=self)

    
    async def shoot(self, interaction):
        self.rock.disabled = True
        self.paper.disabled = True
        self.scissors.disabled = True
        content = f"Rock Paper Scissors...\n" \
                  f"**{dcu.member_name(self.player1)}** picked {self.game['player1']}\n" \
                  f"**{dcu.member_name(self.player2)}** picked {self.game['player2']}\n"

        if ranking[self.game["player1"]] == self.game["player2"]:
            content += f"\n**{self.player1.mention} wins!**"
            await interaction.response.edit_message(content=content, view=self)
        elif ranking[self.game["player2"]] == self.game["player1"]:
            content += f"\n**{self.player2.mention} wins!**"
            await interaction.response.edit_message(content=content, view=self)
        else:
            content += "\n**It's a tie!**"
            await interaction.response.edit_message(content=content, view=self)




    
class rps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rps(self, ctx):
        if ctx.author.bot:
            return

        # Requires view to be called prior to sending in order to access self.message in on_timeout
        if len(ctx.message.mentions) == 1:
            view = RPS_View(ctx.author, player2=ctx.message.mentions[0])
            view.message = await ctx.send("Rock Paper Scissors...", view=view)
        else:
            view = RPS_View(ctx.author)
            view.message = await ctx.send("Rock Paper Scissors...", view=view)



async def setup(bot):
    await bot.add_cog(rps(bot))