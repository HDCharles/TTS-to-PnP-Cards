
# make exe
# nuitka --onefile --enable-plugin=tk-inter --windows-icon-from-ico=TTStoPnp.ico --windows-console-mode=disable --lto=yes --remove-output TTStoPnp.py

from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import re

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


def is_blank_card(card):
    """Check if a card is blank (all pixels are zero or nearly zero)"""
    # Get bounding box of non-zero content; returns None if image is empty/blank
    # Convert to RGB first to ignore alpha channel
    rgb = card.convert("RGB")
    bbox = rgb.getbbox()
    return bbox is None


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

    # Determine if output is JPEG (doesn't support alpha)
    lower_filename = filename.lower()
    is_jpeg = lower_filename.endswith(".jpg") or lower_filename.endswith(".jpeg")

    # Create a new blank page (white background)
    # Use RGB for JPEG output, otherwise match input mode
    if is_jpeg:
        mode = "RGB"
    else:
        mode = image.mode if image.mode in ("RGB", "RGBA") else "RGB"
    
    pageWidth = cardWidth * 3 + 2
    pageHeight = cardHeight * 3 + 2
    
    if mode == "RGBA":
        page = Image.new(mode, (pageWidth, pageHeight), (255, 255, 255, 255))
    else:
        page = Image.new(mode, (pageWidth, pageHeight), (255, 255, 255))

    # Convert source image to matching mode for pasting
    if is_jpeg and image.mode == "RGBA":
        # Composite RGBA onto white background to convert properly
        image = image.convert("RGB")

    for i in range(rows):
        for j in range(cols):
            # Crop the card from the source image
            left = j * cardWidth
            upper = i * cardHeight
            right = (j + 1) * cardWidth
            lower = (i + 1) * cardHeight
            card = image.crop((left, upper, right, lower))

            # Check if card has content (not blank)
            if not is_blank_card(card):
                # Calculate paste position
                paste_x = cardCol * (cardWidth + 1)
                paste_y = cardRow * (cardHeight + 1)
                page.paste(card, (paste_x, paste_y))
                cardCol, cardRow = nextCardLocation(cardCol, cardRow)

            # If filled up page or about to exit, save the page
            if (cardCol == 0 and cardRow == 0) or (i == rows - 1 and j == cols - 1):
                page.save(
                    os.path.join(directory, "sep" + str(count) + "-" + filename)
                )
                count += 1
                # Create fresh page
                if mode == "RGBA":
                    page = Image.new(mode, (pageWidth, pageHeight), (255, 255, 255, 255))
                else:
                    page = Image.new(mode, (pageWidth, pageHeight), (255, 255, 255))

    return count


def separate():
    imageList = top.imageList
    num = 0
    failed_files = []
    
    for i, filename in enumerate(imageList):
        try:
            cols = int(top.dimCol[i].get())
            rows = int(top.dimRow[i].get())
        except ValueError:
            continue
        if cols > 0 and rows > 0:
            imagePath = os.path.join(top.dir, filename)
            try:
                image = Image.open(imagePath)
                num += separateImage(image, top.dir, filename, rows, cols)
                image.close()
            except Exception as e:
                failed_files.append(f"{filename}: {str(e)}")
    
    # Show results
    if failed_files:
        error_msg = "The following files could not be processed:\n\n" + "\n".join(failed_files)
        if num > 0:
            tk.messagebox.showwarning(
                "Completed with Errors",
                f"Created {num} images.\n\n{error_msg}"
            )
        else:
            tk.messagebox.showerror("Error", error_msg)
    else:
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
    top.thumbnails = []  # Keep references to prevent garbage collection

    show_thumbs = top.showThumbnails.get()

    # Header row
    col_offset = 1 if show_thumbs else 0
    if show_thumbs:
        tk.Label(top.scrollFrame, text="", width=6).grid(row=0, column=0)  # Thumbnail column
    tk.Label(top.scrollFrame, text="Image", font=("TkDefaultFont", 9, "bold")).grid(
        row=0, column=col_offset, sticky="w", padx=5
    )
    tk.Label(top.scrollFrame, text="Rows", font=("TkDefaultFont", 9, "bold")).grid(
        row=0, column=col_offset + 1, padx=5
    )
    tk.Label(top.scrollFrame, text="Cols", font=("TkDefaultFont", 9, "bold")).grid(
        row=0, column=col_offset + 2, padx=5
    )

    for i, imageName in enumerate(top.imageList):
        # Create thumbnail if enabled
        if show_thumbs:
            try:
                imagePath = os.path.join(top.dir, imageName)
                img = Image.open(imagePath)
                img.thumbnail((50, 50))  # Resize to max 50x50
                photo = ImageTk.PhotoImage(img)
                top.thumbnails.append(photo)  # Keep reference
                thumb_label = tk.Label(top.scrollFrame, image=photo)
                thumb_label.grid(row=i + 1, column=0, padx=2, pady=2)
                img.close()
            except Exception:
                # If thumbnail fails, just show empty space
                tk.Label(top.scrollFrame, text="", width=6).grid(row=i + 1, column=0)

        # Truncate long filenames for display
        displayName = imageName if len(imageName) <= 40 else imageName[:37] + "..."
        tk.Label(top.scrollFrame, text=displayName).grid(
            row=i + 1, column=col_offset, sticky="w", padx=5
        )

        dimRow.append(tk.Entry(top.scrollFrame, width=5))
        dimCol.append(tk.Entry(top.scrollFrame, width=5))
        dimRow[i].grid(row=i + 1, column=col_offset + 1, padx=5, pady=1)
        dimCol[i].grid(row=i + 1, column=col_offset + 2, padx=5, pady=1)
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

# Thumbnail toggle
top.showThumbnails = tk.BooleanVar(value=False)

def toggleThumbnails():
    if hasattr(top, 'dir') and top.dir:
        setupSelector()

thumbFrame = tk.Frame(top)
thumbCheck = tk.Checkbutton(
    thumbFrame, 
    text="Show thumbnails", 
    variable=top.showThumbnails,
    command=toggleThumbnails
)
thumbCheck.pack()
thumbFrame.pack(pady=2)

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