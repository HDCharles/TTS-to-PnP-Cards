#!/usr/bin/python

from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import os
import re
import numpy

top = tk.Tk()
dirButtons = tk.Frame(top)
top.title("TTStoPnp")
text = tk.Text(top)


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
    page = numpy.ones((cardHeight * 3 + 2, cardWidth * 3 + 2, 3)) * 255
    for i in range(7):
        for j in range(10):
            card = imgData[
                i * cardHeight : (i + 1) * cardHeight,
                j * cardWidth : (j + 1) * cardWidth,
                :,
            ]
            if card.sum() > 0:
                page[
                    cardRow * (cardHeight + 1) : cardRow * (cardHeight + 1)
                    + cardHeight,
                    cardCol * (cardWidth + 1) : cardCol * (cardWidth + 1) + cardWidth,
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
                page = numpy.ones((cardHeight * 3 + 2, cardWidth * 3 + 2, 3)) * 255
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
    tk.messagebox.showinfo("Done", "Separated " + str(num) + " images")


def selectDir(top):
    top.dir = tk.filedialog.askdirectory(initialdir="/", title="Select Directory",)
    text.delete(1.0, tk.END)
    text.insert(tk.INSERT, "dir: " + top.dir)
    text.insert(tk.INSERT, "\nImages to Separate: ")
    for image in getImages(top.dir):
        text.insert(tk.INSERT, "\n" + image)
    text.pack()


def useCurDir(top):
    top.dir = os.getcwd()
    text.delete(1.0, tk.END)
    text.insert(tk.INSERT, "dir: " + top.dir)
    text.insert(tk.INSERT, "\nImages to Separate: ")
    for image in getImages(top.dir):
        text.insert(tk.INSERT, "\n" + image)
    text.pack()


sep = tk.Button(top, text="Separate Images", command=buttonPress)
select = tk.Button(top, text="Select Directory", command=lambda: selectDir(top))
useCur = tk.Button(top, text="Use Current Directory", command=useCurDir(top))

dirButtons.pack()
select.pack(in_=dirButtons, side=tk.LEFT)
useCur.pack(in_=dirButtons, side=tk.RIGHT)
sep.pack()

top.mainloop()
