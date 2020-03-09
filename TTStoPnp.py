#!/usr/bin/python

from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import os
import re
import numpy

top = tk.Tk()
top.dir = tk.filedialog.askdirectory(initialdir="/", title="Select Directory",)

# Code to add widgets will go here...

imageHeight = 3640
imageWidth = 3720
cardHeight = int(imageHeight / 7)
cardWidth = int(imageWidth / 10)


def checkSize(image):
    width, height = image.size
    return width == imageWidth and height == imageHeight


def nextCardLocation(cardCol, cardRow):
    cardCol += 1
    if cardCol == 3:
        cardRow += 1
        cardCol = 0
    if cardRow == 3:
        cardRow = 0
    return cardCol, cardRow


def separateImage(image, directory, filename):
    cardCol = 0
    cardRow = 0
    count = 0
    imgData = numpy.asarray(image)
    page = numpy.ones((cardHeight * 3, cardWidth * 3, 3)) * 255
    for i in range(7):
        for j in range(10):
            card = imgData[
                i * cardHeight : (i + 1) * cardHeight - 1,
                j * cardWidth : (j + 1) * cardWidth - 1,
                :,
            ]
            if card.sum() > 0:
                page[
                    cardRow * cardHeight : (cardRow + 1) * cardHeight - 1,
                    cardCol * cardWidth : (cardCol + 1) * cardWidth - 1,
                    :,
                ] = card
                cardCol, cardRow = nextCardLocation(cardCol, cardRow)
            if (cardCol == 0 and cardRow == 0) or (
                i == 7 - 1 and j == 10 - 1
            ):  # if filled up image or about to exit
                imagePage = Image.fromarray(page.astype(numpy.uint8))
                imagePage.save(
                    os.path.join(directory, "sep" + str(count) + "-" + filename)
                )
                count += 1
                page = numpy.ones((cardHeight * 3, cardWidth * 3, 3)) * 255
    return count


def getImages(directory):
    imageList = []
    for filename in os.listdir(directory):
        if re.search(".*\.png", filename) or re.search(".*\.jpeg", filename):
            imageList.append(filename)
    return imageList


def buttonPress():
    imageList = getImages(top.dir)
    num = 0
    for filename in imageList:
        imagePath = os.path.join(top.dir, filename)
        image = Image.open(imagePath)
        if checkSize(image):
            num += separateImage(image, top.dir, filename)
    tk.messagebox.showinfo(
        "Done", "Separated " + str(num) + " Files, created pages: " + str(imageList)
    )


b1 = tk.Button(top, text="Separate Images", command=buttonPress)

b1.pack()
top.mainloop()
