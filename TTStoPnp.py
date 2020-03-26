#!/usr/bin/python

from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import os
import re
import numpy

top = tk.Tk()
top.title("TTStoPnp")

"""imageHeight = 3640
imageWidth = 3720
cardHeight = int(imageHeight / 7)
cardWidth = int(imageWidth / 10)"""

# this is executed by default
def useCurDir():
    top.dir = os.getcwd()
    # setupText()
    setupSelector()


def selectDir():
    top.dir = tk.filedialog.askdirectory(initialdir="/", title="Select Directory",)
    # setupText()
    setupSelector()


def setupText():
    text.delete(1.0, tk.END)
    text.insert(tk.INSERT, "dir: " + top.dir)
    text.pack()

    # setupSelector()


def getImages():
    directory = top.dir
    imageList = []
    for filename in os.listdir(directory):
        if (
            re.search(".*\.png", filename) or re.search(".*\.jpe{0,1}g", filename)
        ) and not re.search("^sep.*", filename):
            imagePath = os.path.join(directory, filename)
            image = Image.open(imagePath)
            if True:  # checkSize(image):
                imageList.append(filename)
    top.imageList = imageList


"""
def checkSize(image):
    width, height = image.size
    return width == imageWidth and height == imageHeight"""


def separateImage(image, directory, filename, rows, cols):
    def nextCardLocation(cardCol, cardRow):
        cardCol += 1
        if cardCol == 3:
            cardRow += 1
            cardCol = 0
        if cardRow == 3:
            cardRow = 0
        return cardCol, cardRow

    imageWidth, imageHeight = image.size

    cardHeight = int(imageHeight / rows)
    cardWidth = int(imageWidth / cols)

    cardCol = 0
    cardRow = 0
    count = 0
    imgData = numpy.asarray(image)
    page = numpy.ones((cardHeight * 3 + 2, cardWidth * 3 + 2, 3)) * 255
    for i in range(rows):
        for j in range(cols):

            card = imgData[
                i * cardHeight : (i + 1) * cardHeight,
                j * cardWidth : (j + 1) * cardWidth,
                :,
            ]
            print(i, j, card.sum())
            if card.sum() > 0:
                page[
                    cardRow * (cardHeight + 1) : cardRow * (cardHeight + 1)
                    + cardHeight,
                    cardCol * (cardWidth + 1) : cardCol * (cardWidth + 1) + cardWidth,
                    :,
                ] = card
                cardCol, cardRow = nextCardLocation(cardCol, cardRow)
            if (cardCol == 0 and cardRow == 0) or (
                i == rows - 1 and j == cols - 1
            ):  # if filled up image or about to exit
                imagePage = Image.fromarray(page.astype(numpy.uint8))
                imagePage.save(
                    os.path.join(directory, "sep" + str(count) + "-" + filename)
                )
                count += 1
                page = numpy.ones((cardHeight * 3 + 2, cardWidth * 3 + 2, 3)) * 255
    return count


def separate():
    imageList = top.imageList
    num = 0
    for i, filename in enumerate(imageList):
        cols = int(top.dimCol[i].get())
        rows = int(top.dimRow[i].get())
        if cols > 0 and rows > 0:
            imagePath = os.path.join(top.dir, filename)
            image = Image.open(imagePath)
            num += separateImage(image, top.dir, filename, rows, cols)
    tk.messagebox.showinfo("Done", "Created " + str(num) + " Images")


def setupSelector():
    tk.Label(top.dirMsg, text="Dir: " + top.dir).grid(row=0)

    imageSelector = top.imageSelector
    for child in imageSelector.winfo_children():
        child.destroy()
    getImages()
    dimCol = []
    dimRow = []
    tk.Label(imageSelector, text="rows").grid(row=0, column=1)
    tk.Label(imageSelector, text="columns").grid(row=0, column=2)
    for i, imageName in enumerate(top.imageList):
        tk.Label(imageSelector, text=imageName).grid(row=i + 1)
        dimCol.append(tk.Entry(imageSelector))
        dimRow.append(tk.Entry(imageSelector))
        dimCol[i].grid(row=i + 1, column=2)
        dimRow[i].grid(row=i + 1, column=1)
        dimCol[i].insert(10, 0)
        dimRow[i].insert(10, 0)
    top.dimCol = dimCol
    top.dimRow = dimRow


# top.dirmessage = False
top.imageSelector = tk.Frame(top)
top.dirMsg = tk.Frame(top)


comButtons = tk.Frame(top)
sep = tk.Button(top, text="Separate Images", command=lambda: separate())
helpButton = tk.Button(
    top,
    text="Help",
    command=lambda: tk.messagebox.showinfo(
        "Instructions",
        "1) Select your desired directory\n2) Input each image's card dimensions\n3) Leave 0,0 for images you wish to ignore \nNote: images with names that start with 'sep' are ignored",
    ),
)
sep.pack(in_=comButtons, side=tk.LEFT)
helpButton.pack(in_=comButtons, side=tk.RIGHT)

dirButtons = tk.Frame(top)
select = tk.Button(top, text="Select Directory", command=lambda: selectDir())
useCur = tk.Button(top, text="Use Current Directory", command=useCurDir())
select.pack(in_=dirButtons, side=tk.LEFT)
useCur.pack(in_=dirButtons, side=tk.RIGHT)

top.dirMsg.pack()
top.imageSelector.pack()
comButtons.pack()
dirButtons.pack()

top.mainloop()
