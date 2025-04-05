from PIL import Image, ImageDraw, ImageFont
import requests
import moviepy.editor as mpe
from pydub import AudioSegment
from gtts import gTTS
import numpy as np
import io
import datetime
import os
import string

cwd = os.path.dirname(__file__)

bg_gray = (66, 69, 73)

circlemask = Image.open(cwd + "/images/circle.png").convert("L")
transparent = Image.new('RGBA', (184, 184), color=bg_gray)

base = ImageFont.truetype(cwd + '/Whitney/whitneymedium.otf', 20)
bold = ImageFont.truetype(cwd + '/Whitney/whitneysemibold.otf', 20)
italic = ImageFont.truetype(cwd + '/Whitney/whitneymediumitalic.otf', 20)
time_font = ImageFont.truetype(cwd + '/Whitney/whitneybook.otf', 14)


def get_text_dimensions(text, font=base):
    ascent, descent = font.getmetrics()
    try:
        text_width = font.getmask(text).getbbox()[2]
        text_height = font.getmask(text).getbbox()[3] + descent
    except TypeError:
        print("TEXT DIMENSION ERROR:", text)
        text_width, text_height = 0, 0

    return text_width, text_height



class DrawMessage:

    content = None
    username = None
    pfp = None
    name_color = None
    time = None

    def __init__(self, content, username, url, name_color, time, baseImg=None):
        if baseImg is None:
            self.content = content
            self.username = username
            pfp = Image.open(io.BytesIO(requests.get(url).content))
            self.pfp = pfp.convert("RGBA")
            self.name_color = name_color

            self.time = time
            self.time = self.time + datetime.timedelta(hours=-5)
            self.size = (600, 83)
            self.width, self.height = self.size

        else:
            self.content = content

            self.size = (600, baseImg.height+25)
            self.width, self.height = self.size


        self.baseImg = baseImg
        self.output = None
        self.draw = None

        if baseImg is None:
            self.make_text()
            self.make_pfp()
            self.make_name()
        else:
            self.make_text(start=self.baseImg.height-25)


    def format_text(self, content):
        texts = content.split("\n")
        newText = ""
        for text in texts:
            split = text.split()
            width = 0

            for word in split:
                if any(i not in string.printable for i in word):
                    continue
                w = base.getmask(word).getbbox()[2]

                # Add text normally as long as it is below 500 px wide
                if width + w < 500:
                    newText += word + " "
                    width += w + 4

                # If 1 word is too long, break it down into 480 px wide chunks
                elif w > 500:
                    if len(newText) > 0:
                        newText += "\n"
                    start = 0
                    end = 30
                    while end < len(word):
                        while get_text_dimensions(word[start:end])[0] <= 480:
                            end += 1                        # Increase segment length until surpasses 480 pixels
                            if end == len(word):            # End loop once it hits the word length
                                break

                        newText += word[start:end] + "\n"
                        start = end                         # Add slice of word to output string
                        end += 1                            # Restart loop at the end of previous segment

                # If normal text extends past 500, add newline and return to width 0
                else:
                    newText += "\n" + word + " "
                    width = w
                    self.height += 25

            # Add newline for each separated message in 'texts'
            newText += "\n"

        return newText

    def make_text(self, start=33):
        txt = self.format_text(self.content)
        numLines = txt.count('\n') - 1

        if self.baseImg is None:
            self.output = Image.new("RGB", (self.width, self.height + 25*numLines), bg_gray)

        else:
            self.output = Image.new("RGB", (self.width, self.height + 25*numLines), bg_gray)
            self.output.paste(self.baseImg)

        self.draw = ImageDraw.Draw(self.output)

        self.draw.text((80, start), txt, font=base, fill=(255, 255, 255))

    def make_pfp(self):
        self.pfp.thumbnail((50, 50))
        transparent.thumbnail(self.pfp.size)
        circlemask.thumbnail(self.pfp.size)

        img = Image.composite(self.pfp, transparent, circlemask)
        img.putalpha(circlemask)

        self.output.paste(img, (10, 10))

    def make_name(self):
        dims = get_text_dimensions(self.username, base)
        self.draw.text((80, 7), self.username, font=base, fill=self.name_color)

        time_diff = datetime.datetime.now().date() - self.time.date()

        if str(time_diff)[:2] == '1 ':
            timef = "Yesterday at " + self.time.strftime("%#I:%M %p")
        elif str(time_diff)[0] == '0':
            timef = "Today at " + self.time.strftime("%#I:%M %p")
        else:
            timef = self.time.strftime("%m/%d/%Y")

        self.draw.text((90 + dims[0], 13), timef, font=time_font, fill=(126, 129, 133))




class MakeVideo:

    def __init__(self, clips):
        self.images = clips
        self.durations = []
        self.video = None
        self.audio = None

    def resize_clips(self):
        heights = []
        for clip in self.images:
            heights.append(clip.height)

        max_height = max(heights)
        new_clips = []
        for clip in self.images:
            pad = Image.new("RGB", (600, max_height), (0, 0, 0))
            top = (pad.height - clip.height) / 2
            pad.paste(clip, (0, int(top)))
            new_clips.append(pad)

        self.images = new_clips
        return new_clips

    def convert_videofiles(self, durations):
        videofiles = []
        self.resize_clips()
        for i in range(len(self.images)):
            image = np.array(self.images[i])
            video = mpe.ImageClip(image, duration=durations[i])
            videofiles.append(video)

        self.video = mpe.concatenate_videoclips(videofiles)
        return self.video

    def get_audiofile(self, texts):
        audiofiles = []
        self.durations = []
        self.audio = []
        for i in range(len(self.images)):
            audiobytes = io.BytesIO()
            audio = gTTS(text=texts[i])
            audio.write_to_fp(audiobytes)

            audiobytes.seek(0, 0)
            audiofile = AudioSegment.from_file(audiobytes)
            audiofiles.append(audiofile)
            self.durations.append(audiofile.duration_seconds)

        fullAudio = sum(audiofiles)
        fullAudio.export(cwd + "/images/output.wav")
        self.audio = mpe.AudioFileClip(cwd + "/images/output.wav")

        return self.audio

    def add_tts_sound(self, texts):
        audio = self.get_audiofile(texts)

        video = self.convert_videofiles(self.durations)
        video.audio = audio
        video = video.subclip(0, video.duration - 0.2)

        return video






















