import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import re
import json
import DiscordTTS
from io import BytesIO
import pathlib
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GENAI"))
model = genai.GenerativeModel("gemini-1.5-flash")
pdir = pathlib.Path(__file__).parent.parent.resolve()

def to_string(msg):
    return f"[MessageID: {msg.id}]] {msg.author.name} at {msg.created_at.strftime('%H:%M')}: {msg.content}"

def get_wrapped_text(text: str, font: ImageFont.ImageFont, line_length: int):
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return '\n'.join(lines)

def justify_text(draw, font, text, pos, width):
    x, y = pos
    for line in text.split("\n"):
        words = line.split(" ")
        words_length = sum(draw.textlength(w, font=font) for w in words)
        space_length = (width - words_length) / (len(words))
        x = pos[0]
        for word in words:
            draw.text((x, y), word, font=font, fill="black")
            x += draw.textlength(word, font=font) + space_length
        y += 23
    return y

# Input is a list of Discord Message objects
def build_images(messages):
    pics = []
    temp = []

    # Combine messages from the same author into one
    previousAuthor = None
    for msg in messages:
        if msg.author == previousAuthor:
            prev = temp[-1]
            prev.content += "\n" + msg.content
        else:
            temp.append(msg)
        previousAuthor = msg.author


    for msg in temp:
        if len(msg.clean_content) == 0:
            continue
        content = msg.clean_content
        pfp = msg.author.avatar.url  # (format="png", size=4096).read()
        name_color = msg.author.color.to_rgb()
        if name_color == (0, 0, 0):
            name_color = (255, 255, 255)
        time = msg.created_at

        # Get Discord username if user has no nickname
        username = msg.author.nick
        if username is None:
            username = msg.author.name

        # Call DrawMessage and save output to list
        img = DiscordTTS.DrawMessage(content, username, pfp, name_color, time).output
        pics.append(img)

    return pics




class newspaper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def newspaper(self, ctx):
        califr = pdir / 'images' / 'califr.ttf'
        timesbd = pdir / 'images' / 'timesbd.ttf'
        paperimg = pdir / 'images' / 'Newspaper.png'
        msgs = []
        channel = ctx.channel

        if channel.id == 750765122821161073:
            channel = self.bot.get_channel(810335368900771894)

        start = datetime.combine(datetime.date(datetime.now()), datetime.min.time())
        # start = start.replace(tzinfo=pytz.timezone("America/New_York"))

        # Get previous day until len msgs > 50
        while not msgs:
            # Add all messages from current day to list
            async for msg in channel.history(limit=None, after=start, before=(start + timedelta(days=1))):
                if msg.content != '' and not msg.author.bot:
                    msgs.append(to_string(msg))
            # Reset messages if there are less than 50, go back a day
            if len(msgs) < 50:
                msgs = []
                start -= timedelta(days=1)

        # Generate 3 newspaper articles and load as json
        response = model.generate_content(
            "You are to create a JSON formatted output for humorous and teasing newspaper articles. Given the following message history, write 3 headlines and a brief story along with it. Try and choose different topics for each article. Format them 'headline' and 'story' as a list of 'articles'." + "\n".join(msgs))
        try:
            answer = re.search(r'{(\s*.*)+}', response.text).group()
            form = json.loads(answer)
        except json.decoder.JSONDecodeError:
            print(response)
            return

        # Import newspaper image template
        image = Image.open(paperimg)
        draw = ImageDraw.Draw(image)

        # THREE ARTICLES
        for i in range(3):
            # Wrap headline and write to columns
            font = ImageFont.truetype(timesbd, 22)
            wrapped_text = get_wrapped_text(form["articles"][i]["headline"], font, line_length=250)
            height = justify_text(draw, font, wrapped_text, (20 + (290 * i), 425), 270)

            # Wrap story and write to column below headline (at height)
            font = ImageFont.truetype(timesbd, 20)
            wrapped_text = get_wrapped_text(form["articles"][i]["story"], font, line_length=250)
            justify_text(draw, font, wrapped_text, (20 + (290 * i), height), 270)

        # MAIN HEADLINE AND IMAGE
        response = model.generate_content(
            "You are to create a JSON formatted output for this prompt. Given the following messages, pick the funniest 7 consecutive messages and write a short headline for them. Format the output as 'headline' and 'messages.' The messages should just be a list of message IDs." + "\n".join(msgs))
        try:
            answer = re.search(r'{(\s*.*)+}', response.text).group()
            form = json.loads(answer)
        except json.decoder.JSONDecodeError:
            print(response)
            return

        # Write paper date
        date = start.strftime("%A, %B") + f" {start.day} {start.year}"
        font = ImageFont.truetype(califr, 32)
        dims = DiscordTTS.get_text_dimensions(date, font=font)
        draw.text((720 - dims[0] // 2, 192), date, font=font, fill="black")

        # Write main headline
        font = ImageFont.truetype(califr, 100)
        dims = DiscordTTS.get_text_dimensions(form["headline"], font=font)
        if dims[0] > image.size[0]:
            font = ImageFont.truetype(califr, (image.size[0] - 150) * 100 // dims[0])
        justify_text(draw, font, form["headline"], (20, 270), image.size[0] - 40)

        # Collect Message objects from AI output
        sequence = [await channel.fetch_message(msgid) for msgid in form["messages"]]
        images = build_images(sequence)
        widths, heights = zip(*(i.size for i in images))

        total_width = max(widths)
        max_height = sum(heights)

        new_im = Image.new('RGB', (total_width, max_height))

        y_offset = 0
        for im in images:
            new_im.paste(im, (0, y_offset))
            y_offset += im.size[1]

        if new_im.size[1] > 600:
            new_im = new_im.resize((500, 600))
        else:
            new_im = new_im.resize((500, new_im.size[1]))

        image.paste(new_im, (900, 440))

        fileobj = BytesIO()
        image.save(fileobj, "png")
        fileobj.seek(0)

        await ctx.channel.send(file=discord.File(fileobj, filename="newspaper.png"))



async def setup(bot):
    await bot.add_cog(newspaper(bot))
