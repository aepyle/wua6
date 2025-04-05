import discord
from discord import ui
from discord.ext import commands

games = {}




class HangmanInit(ui.Modal, title="Hangman"):
    text_input = ui.TextInput(label="Enter the Answer", placeholder="Only letters allowed", min_length=1)
    interaction = None

    async def on_submit(self, interaction):
        answer = self.text_input.value.upper()
        self.answer = answer
        if interaction.message.id not in games.keys():
            if answer.replace(" ", "").isalpha():
                games[interaction.message.id] = {"answer": answer.upper(),
                                                 "guesses": 0,
                                                 "lettersRight": [],
                                                 "lettersWrong": [],
                                                 "victory": False}
                await interaction.response.defer()
                self.stop()
                self.interaction = interaction
            else:
                await interaction.response.defer()

        else:
            if answer.replace(" ", "").isalpha():
                game = games[interaction.message.id]

                if answer in game["lettersRight"] or answer in game["lettersWrong"]\
                        or (len(answer) > 1 and len(answer) != len(game["answer"])):
                    self.answer = '0'
                    await interaction.response.defer()
                    return
                elif len(answer) == 1 and answer in game["answer"] and answer not in game["lettersRight"]:
                    game["lettersRight"].append(answer)
                elif len(answer) == 1 and answer not in game["answer"] and answer not in game["lettersWrong"]:
                    game["lettersWrong"].append(answer)
                    game["guesses"] += 1
                else:
                    if len(answer) == len(game["answer"]):
                        if answer == game["answer"]:
                            game["victory"] = True
                        else:
                            if answer not in game["lettersWrong"]:
                                game["lettersWrong"].append(answer)
                                game["guesses"] += 1

                await interaction.response.defer()
                self.stop()
                self.interaction = interaction

            else:
                await interaction.response.defer()


        



class HangmanButton(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=None)
        self.author = author

    @discord.ui.button(label="Enter Answer", style=discord.ButtonStyle.blurple)
    async def hangman(self, interaction, button):
        if interaction.user == self.author and interaction.message.id not in games.keys():
            modal_cls = HangmanInit()
            await interaction.response.send_modal(modal_cls)
            # If interaction responds and does not time out
            if not await modal_cls.wait() and modal_cls.answer.replace(' ', '').isalpha():
                button.label = "Enter Guess"
                button.style = discord.ButtonStyle.green

                embed = await self.create_embed(interaction.message.id)
                await interaction.edit_original_response(content="", embed=embed, view=self)

        elif interaction.message.id in games.keys():
            modal_ans = HangmanInit()
            await interaction.response.send_modal(modal_ans)
            if not await modal_ans.wait():
                if not modal_ans.answer.replace(' ', '').isalpha():
                    return
                embed = await self.create_embed(interaction.message.id)
                if len(embed.fields) == 4:
                    self.clear_items()
                await interaction.edit_original_response(
                    content=f"{modal_ans.interaction.user.mention} guessed {modal_ans.answer}", embed=embed, view=self)



    async def create_embed(self, msgid):
        game = games[msgid]
        word = ["\_" for letter in game["answer"]]
        for i in range(len(game["answer"])):
            if game["answer"][i] in game["lettersRight"]:
                word[i] = game["answer"][i]
            if game["answer"][i] == ' ':
                word[i] = '᲼'

        word = " ".join(word)
        if '_' not in word:
            game["victory"] = True

        right = ""
        for letter in game["lettersRight"]:
            if len(letter) == 1:
                right += f"{letter} "

        wrong = ""
        extra = ""
        for letter in game["lettersWrong"]:
            if len(letter) == 1:
                wrong += f"{letter} "
            if len(letter) > 1:
                extra += f"\n{letter}"
        wrong += extra

        embed = discord.Embed(title="Hangman", color=0x2ecc71)
        embed.description = "```" + ascii_man[game['guesses']] + "```"
        embed.add_field(name="Word:", value=f"**{word}**")
        embed.add_field(name="Correct:", value=right, inline=False)
        embed.add_field(name="Incorrect:", value=wrong, inline=False)

        if game["victory"] is True:
            embed.add_field(name="**_You Won!_**", value=f"The answer was **{game['answer']}**", inline=False)
            del games[msgid]
        elif game["guesses"] == 7:
            embed.add_field(name="**_You Lost!_**", value=f"The answer was **{game['answer']}**", inline=False)
            del games[msgid]

        return embed








class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hangman(self, ctx):
        await ctx.send("Press button to begin", view=HangmanButton(author=ctx.author))







ascii_man = [''' 
   +---+
       |
       |
       |
       |
       |
==========''', '''
   +---+
   |   |
       |
       |
       |
       |
==========''', '''
   +---+
   |   |
   O   |
       |
       |
       |
==========''', '''
   +---+
   |   |
   O   |
   |   |
       |
       |
==========''', '''
   +---+
   |   |
   O   |
  /|   |
       |
       |
==========''', '''
   +---+
   |   |
   O   |
  /|\\  |
       |
       |
==========''', '''
   +---+
   |   |
   O   |
  /|\\  |
  /    |
       |
==========''', '''
   +---+
   |   |
   O   |
  /|\\  |
  / \\  |
       |
==========''']




async def setup(bot):
    await bot.add_cog(Hangman(bot))