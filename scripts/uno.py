# -*- coding: utf8 -*-


from PIL import Image, ImageFont, ImageDraw
import os
import random
import requests
from copy import copy

unoFolder = os.path.dirname(__file__) + "/Uno Cards/"
template = Image.open(unoFolder + "background.png")
baseCard = Image.open(unoFolder + "base.png")
blankCard = Image.open(unoFolder + "blank.png").resize((100, 155))
pfpBorder = Image.open(unoFolder + "pfp border.png")


def Center(number):
    return int(number/2)


def AddTuple(tuple1, tuple2):
    outTuple = []
    if len(tuple1) == len(tuple2):
        for i in range(0, len(tuple1)):
            outTuple.append(list(tuple1)[i] + list(tuple2)[i])

    else:
        raise IndexError("Added tuples not of same size")
    return tuple(outTuple)

class Uno:

    center = template.width / 2
    cardCenter = baseCard.width / 2

    centerCard =   ["", 0]
    players =      []
    playerOrder =  []
    playerTurn =   0
    rotation =     True
    toDraw =       0
    playersHands = []
    cardDeck = {}


    def __init__(self, players):
        if len(players) < 2:                                            # If less than 2 players, game cannot start
            print("Minimum of 2 players required")  # to message.send
            return

        self.players = players

        self.Start()



    def Card(self, card):
        if card[1] == "":                                                                       # If suit is only input
            return Image.open(self.unoFolder + card[0] + ".png")                                # Then return suit image

        baseImg = Image.open(self.unoFolder + card[0] + ".png")                                 # Get card suit image
        valueImg = Image.open(self.unoFolder + card[1] + ".png")

        cornerValueImg = valueImg.resize((int(valueImg.width/2.2), int(valueImg.height/2.2)))   # Resizes value image
        rotatedValueImg = cornerValueImg.rotate(180)                                            # Rotates resized value image

        baseWidth, baseHeight = baseImg.size                                                    # Get card suit image width, height
        valueWidth, valueHeight = valueImg.size                                                 # Get card value image width, height

        cardCenter = (int((baseWidth - valueWidth) / 2), int((baseHeight - valueHeight) / 2))   # Calculate position for center of the card
        topLeftCorner = (int(0.1 * baseImg.width), int(0.06 * baseImg.height))                  # Calculate position for top left corner
        bottomRightCorner = (int(0.7 * baseImg.width), int(0.74 * baseImg.height))              # Calculate position for bottom right corner

        baseImg.paste(valueImg, box=cardCenter, mask=valueImg)                                  # Paste value on suit image
        baseImg.paste(cornerValueImg, box=topLeftCorner, mask=cornerValueImg)                   # Paste resized value on suit image
        baseImg.paste(rotatedValueImg, box=bottomRightCorner, mask=rotatedValueImg)             # Paste rotated value om suit image

        return baseImg                                                                          # Return modified card image



    def AddToHand(self, suit, value):
        self.playersHands[self.playerTurn][suit].append(copy(value))              # Add card [suit, value] to player hand


        try:
            self.playersHands[self.playerTurn][suit].sort()                 # Sort player hand from 0 to 9
        except TypeError or AttributeError:                                                   # Ignore if string is sorted with numbers
            pass



    def Start(self):

        self.centerCard = ["", 0]
        self.playerOrder = []
        self.playerTurn = 0
        self.rotation = True
        self.toDraw = 0
        self.playersHands = []
        self.cardDeck = {
            "red":    ["0", "0", "1", "1", "2", "2", "3", "3", "4", "4", "5", "5", "6", "6", "7", "7", "8", "8", "9", "9", "skip", "skip", "reverse", "reverse", "+2", "+2"],
            "yellow": ["0", "0", "1", "1", "2", "2", "3", "3", "4", "4", "5", "5", "6", "6", "7", "7", "8", "8", "9", "9", "skip", "skip", "reverse", "reverse", "+2", "+2"],
            "blue":   ["0", "0", "1", "1", "2", "2", "3", "3", "4", "4", "5", "5", "6", "6", "7", "7", "8", "8", "9", "9", "skip", "skip", "reverse", "reverse", "+2", "+2"],
            "green":  ["0", "0", "1", "1", "2", "2", "3", "3", "4", "4", "5", "5", "6", "6", "7", "7", "8", "8", "9", "9", "skip", "skip", "reverse", "reverse", "+2", "+2"],
            "wild":   ["", "", "", ""],
            "+4":     ["", "", "", ""]}


        for i in range(0, len(self.players)):
            self.playersHands.append({"red": [],
                                      "yellow": [],
                                      "blue": [],
                                      "green": [],
                                      "wild": [],
                                      "+4": []})
            self.playerOrder.append(i)

            self.Draw(7)                                            # Draw 5 starting cards
            self.playerTurn += 1

        self.playerTurn = 0






        self.centerCard = self.NewCard()                # Randomize card in the center
        while self.centerCard[0] in ["wild", "+4"]:     # If card in the center is wild or +4
            self.centerCard = self.NewCard()            # Then randomize card in the center again

        for hand in self.playersHands:
            print(hand)
        print("End of Start sequence\n\n\n")





    def Display2(self, currentPlayer=playerTurn):                                                     # Shown to one player at all times
        # Change all 0's to current player

        background = Image.open(self.unoFolder + "background.png")
        centerCard = self.Card(self.centerCard)
        centerWidth = int(self.center - self.cardCenter)
        centerHeight = int((self.template.height - self.baseCard.height)/2)

        totalCards = self.SumOfCards(currentPlayer)

        try:
            start = centerWidth - 0.75 * (600 / totalCards * (totalCards - 1))
        except ZeroDivisionError:
            start = centerWidth

        displacement = 0
        for suit in self.playersHands[currentPlayer]:
            for value in self.playersHands[currentPlayer][suit]:
                background.paste(self.Card([suit, value]), box=(int(start + displacement), 750), mask=self.Card([suit, value]))
                displacement += 0.75 * (1200 / totalCards)

        background.paste(centerCard, box=(centerWidth, centerHeight), mask=centerCard)

        displacement = 0
        start = self.center - 120 * len(self.players[2:])


        # Player PFPs
        # Start at current player index and loop around, so that current user is not between other players' PFPs
        for i in range(currentPlayer - len(self.players)+1, currentPlayer):

            try:
                avatarURL = self.players[i].avatar.url
            except AttributeError:
                avatarURL = self.players[i].default_avatar.url
            playerPFP = Image.open(requests.get(avatarURL, stream=True).raw)
            playerPFP = playerPFP.resize((120, 120))

            if self.players[i] == self.players[self.playerTurn]:
                background.paste(self.pfpBorder, box=(int(start + displacement - playerPFP.width / 2) - 15, 45), mask=self.pfpBorder)
            background.paste(playerPFP, box=(int(start + displacement - playerPFP.width / 2), 60), mask=None)
            background.paste(self.blankCard, box=(int(start + displacement - 50), 200), mask=self.blankCard)

            displacement += 240


        newBackground = ImageDraw.Draw(background)
        font = ImageFont.truetype(self.unoFolder + "OdibeeSans-Regular.ttf", 64)
        displacement = 0
        start = self.center - 120 * len(self.players[2:])

        for i in range(0, len(self.players)):
            if i == currentPlayer:
                continue
            xVal = start + displacement - 20
            newBackground.text((xVal, 250), str(self.SumOfCards(i)), (255, 255, 255), font=font)
            displacement += 240

        if self.toDraw > 0:
            newBackground.text((1500, 450), str("Cards to draw"), (0, 0, 0), font=font)
            newBackground.text((1575, 600), str(self.toDraw), (0, 0, 0), font=font)

        return background




    def NewCard(self):
        totalCards = 0

        for suit in self.cardDeck:
            totalCards += len(self.cardDeck[suit])

        chosenCard = random.randint(0, totalCards - 1)

        cardNum = 0

        for suit in self.cardDeck:
            for i in range(0, len(self.cardDeck[suit])):
                if cardNum == chosenCard:
                    card = [suit, self.cardDeck[suit][i]]
                    self.cardDeck[suit].pop(i)

                    return card

                cardNum += 1


    def Draw(self, quantity=1):
        for i in range(0, quantity):
            card = self.NewCard()
            self.AddToHand(card[0], card[1])


    def PlayCard(self, card):
        success = "success"

        if self.toDraw == -1:
            self.toDraw = 0
            self.NextTurn()
            return "You got skipped"

        if "draw" in card.lower():

            if self.toDraw > 0:
                self.Draw(self.toDraw)
                self.toDraw = 0

            else:
                self.Draw()

            self.NextTurn()
            return success                                         # Change these lines for "draw until playable" setting


        card = card.lower().split()
        if len(card) <= 1:
            return
        suit = card[0]
        value = card[1]


        if self.centerCard[1] == "+2" and value != "+2" and self.toDraw > 0:
            return "Must play a +2 or draw"

        if self.centerCard[1] == "+four" and suit != "+4" and self.toDraw > 0:
            return "Must play a +4 or draw"


        if suit != "wild" and suit != "+4":
            if suit != self.centerCard[0] and value != self.centerCard[1]:
                return "Card does not match"

            if value not in self.playersHands[self.playerTurn][suit]:
                return "Don't have that card"



        if suit == "wild" or suit == "+4":
            if len(self.playersHands[self.playerTurn][suit]) == 0:
                return "Don't have that card"

            if value not in ["red", "yellow", "blue", "green"]:
                return "Not a valid color"


        elif value == "+2":
            self.toDraw += 2

        elif value == "reverse":
            self.rotation = not self.rotation
            self.playerOrder.reverse()

        elif value == "skip":
            self.toDraw = -1


        if suit == "+4":
            self.toDraw += 4
            self.centerCard = [value, "+four"]
            self.playersHands[self.playerTurn][suit].remove("")
        elif suit == "wild":
            self.centerCard = [value, ""]
            self.playersHands[self.playerTurn][suit].remove("")
        else:
            self.playersHands[self.playerTurn][suit].remove(value)
            self.centerCard = [suit, value]

        self.NextTurn()

        if suit == "+4" or suit == "wild":
            self.cardDeck[suit].append("")
        else:
            self.cardDeck[suit].append(value)

        return success





    def NextTurn(self):
        if self.rotation is True:
            self.playerTurn += 1
        else:
            self.playerTurn -= 1


        if self.playerTurn >= len(self.players):
            self.playerTurn = 0
        if self.playerTurn < 0:
            self.playerTurn = len(self.players) - 1

        self.playerOrder.append(self.playerOrder.pop(0))





    def SumOfCards(self, player):
        counter = 0
        for suit in self.playersHands[player]:
            counter += len(self.playersHands[player][suit])
        return counter

