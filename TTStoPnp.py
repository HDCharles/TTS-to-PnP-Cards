#!/usr/bin/python

# make exe with: pyinstaller --onefile --noupx --icon=TTStoPnp.png TTStoPnp.py

from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import os
import re
import numpy

top = tk.Tk()
top.title("TTStoPnp")
top.geometry("500x500")


def useCurDir():
    top.dir = os.getcwd()
    setupSelector()


def selectDir():
    top.dir = tk.filedialog.askdirectory(
        initialdir="/",
        title="Select Directory (files not shown)",
    )
    if top.dir:
        setupSelector()


def getImages():
    directory = top.dir
    imageList = []
    for filename in sorted(os.listdir(directory)):
        if (
            re.search(r".*\.png", filename, re.IGNORECASE) 
            or re.search(r".*\.jpe?g", filename, re.IGNORECASE)
        ) and not re.search(r"^sep.*", filename):
            imagePath = os.path.join(directory, filename)
            try:
                image = Image.open(imagePath)
                image.close()
                imageList.append(filename)
            except Exception:
                pass
    top.imageList = imageList


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
    imageChannels = imgData.shape[2]

    page = numpy.ones((cardHeight * 3 + 2, cardWidth * 3 + 2, imageChannels)) * 255

    for i in range(rows):
        for j in range(cols):
            card = imgData[
                i * cardHeight : (i + 1) * cardHeight,
                j * cardWidth : (j + 1) * cardWidth,
                :,
            ]
            if card[:, :, :3].sum() > 0:
                page[
                    cardRow * (cardHeight + 1) : cardRow * (cardHeight + 1) + cardHeight,
                    cardCol * (cardWidth + 1) : cardCol * (cardWidth + 1) + cardWidth,
                    :,
                ] = card
                cardCol, cardRow = nextCardLocation(cardCol, cardRow)
            if (cardCol == 0 and cardRow == 0) or (
                i == rows - 1 and j == cols - 1
            ):
                imagePage = Image.fromarray(page.astype(numpy.uint8))
                imagePage.save(
                    os.path.join(directory, "sep" + str(count) + "-" + filename)
                )
                count += 1
                page = (
                    numpy.ones((cardHeight * 3 + 2, cardWidth * 3 + 2, imageChannels))
                    * 255
                )
    return count


def separate():
    imageList = top.imageList
    num = 0
    for i, filename in enumerate(imageList):
        try:
            cols = int(top.dimCol[i].get())
            rows = int(top.dimRow[i].get())
        except ValueError:
            continue
        if cols > 0 and rows > 0:
            imagePath = os.path.join(top.dir, filename)
            image = Image.open(imagePath)
            num += separateImage(image, top.dir, filename, rows, cols)
            image.close()
    tk.messagebox.showinfo("Done", "Created " + str(num) + " Images")


def applyToAll():
    """Apply the default row/col values to all images"""
    try:
        defaultRows = top.defaultRows.get()
        defaultCols = top.defaultCols.get()
    except Exception:
        return
    
    for i in range(len(top.imageList)):
        top.dimRow[i].delete(0, tk.END)
        top.dimRow[i].insert(0, defaultRows)
        top.dimCol[i].delete(0, tk.END)
        top.dimCol[i].insert(0, defaultCols)


def clearAll():
    """Reset all values to 0"""
    for i in range(len(top.imageList)):
        top.dimRow[i].delete(0, tk.END)
        top.dimRow[i].insert(0, "0")
        top.dimCol[i].delete(0, tk.END)
        top.dimCol[i].insert(0, "0")


def setupSelector():
    # Update directory label
    for child in top.dirMsg.winfo_children():
        child.destroy()
    tk.Label(top.dirMsg, text="Dir: " + top.dir).pack()

    # Clear existing content in scroll frame
    for child in top.scrollFrame.winfo_children():
        child.destroy()

    getImages()
    dimCol = []
    dimRow = []

    # Header row
    tk.Label(top.scrollFrame, text="Image", font=("TkDefaultFont", 9, "bold")).grid(
        row=0, column=0, sticky="w", padx=5
    )
    tk.Label(top.scrollFrame, text="Rows", font=("TkDefaultFont", 9, "bold")).grid(
        row=0, column=1, padx=5
    )
    tk.Label(top.scrollFrame, text="Cols", font=("TkDefaultFont", 9, "bold")).grid(
        row=0, column=2, padx=5
    )

    for i, imageName in enumerate(top.imageList):
        # Truncate long filenames for display
        displayName = imageName if len(imageName) <= 40 else imageName[:37] + "..."
        tk.Label(top.scrollFrame, text=displayName).grid(
            row=i + 1, column=0, sticky="w", padx=5
        )
        
        dimRow.append(tk.Entry(top.scrollFrame, width=5))
        dimCol.append(tk.Entry(top.scrollFrame, width=5))
        dimRow[i].grid(row=i + 1, column=1, padx=5, pady=1)
        dimCol[i].grid(row=i + 1, column=2, padx=5, pady=1)
        dimRow[i].insert(0, "0")
        dimCol[i].insert(0, "0")

    top.dimCol = dimCol
    top.dimRow = dimRow

    # Update scroll region after adding content
    top.scrollFrame.update_idletasks()
    top.canvas.config(scrollregion=top.canvas.bbox("all"))


def on_mousewheel(event):
    top.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def on_mousewheel_linux(event):
    if event.num == 4:
        top.canvas.yview_scroll(-1, "units")
    elif event.num == 5:
        top.canvas.yview_scroll(1, "units")


# Directory message frame
top.dirMsg = tk.Frame(top)
top.dirMsg.pack(pady=5)

# Directory buttons
dirButtons = tk.Frame(top)
select = tk.Button(dirButtons, text="Select Directory", command=selectDir)
useCur = tk.Button(dirButtons, text="Use Current Directory", command=useCurDir)
select.pack(side=tk.LEFT, padx=5)
useCur.pack(side=tk.LEFT, padx=5)
dirButtons.pack(pady=5)

# Bulk operations frame
bulkFrame = tk.Frame(top)
tk.Label(bulkFrame, text="Set all to:").pack(side=tk.LEFT, padx=2)
tk.Label(bulkFrame, text="Rows:").pack(side=tk.LEFT, padx=2)
top.defaultRows = tk.Entry(bulkFrame, width=5)
top.defaultRows.pack(side=tk.LEFT, padx=2)
top.defaultRows.insert(0, "7")
tk.Label(bulkFrame, text="Cols:").pack(side=tk.LEFT, padx=2)
top.defaultCols = tk.Entry(bulkFrame, width=5)
top.defaultCols.pack(side=tk.LEFT, padx=2)
top.defaultCols.insert(0, "10")
applyBtn = tk.Button(bulkFrame, text="Apply to All", command=applyToAll)
applyBtn.pack(side=tk.LEFT, padx=5)
clearBtn = tk.Button(bulkFrame, text="Clear All", command=clearAll)
clearBtn.pack(side=tk.LEFT, padx=5)
bulkFrame.pack(pady=5)

# Scrollable container for image list
containerFrame = tk.Frame(top)
containerFrame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

top.canvas = tk.Canvas(containerFrame)
scrollbar = tk.Scrollbar(containerFrame, orient="vertical", command=top.canvas.yview)
top.canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
top.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

top.scrollFrame = tk.Frame(top.canvas)
top.canvas.create_window((0, 0), window=top.scrollFrame, anchor="nw")

# Bind mousewheel scrolling (Windows/Mac)
top.canvas.bind_all("<MouseWheel>", on_mousewheel)
# Bind mousewheel scrolling (Linux)
top.canvas.bind_all("<Button-4>", on_mousewheel_linux)
top.canvas.bind_all("<Button-5>", on_mousewheel_linux)

# Command buttons
comButtons = tk.Frame(top)
sep = tk.Button(comButtons, text="Separate Images", command=separate)
helpButton = tk.Button(
    comButtons,
    text="Help",
    command=lambda: tk.messagebox.showinfo(
        "Instructions",
        "1) Select your desired directory\n"
        "2) Input each image's card dimensions (usually 7 rows, 10 cols for TTS)\n"
        "   - Use 'Apply to All' to quickly set common dimensions\n"
        "3) Leave 0,0 for images you wish to ignore\n"
        "4) Click 'Separate Images'\n\n"
        "Note: images with names that start with 'sep' are ignored",
    ),
)
sep.pack(side=tk.LEFT, padx=10)
helpButton.pack(side=tk.LEFT, padx=10)
comButtons.pack(pady=10)

# Initialize with current directory
top.dir = os.getcwd()
top.imageList = []
top.dimCol = []
top.dimRow = []

top.mainloop()
