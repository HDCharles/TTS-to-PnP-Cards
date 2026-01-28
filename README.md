# TTS to PnP Cards
Separates TTS Card Dumps into Printable Images

Run it from any directory, click help for further instructions.
 
Standalone exe available here: https://github.com/HDCharles/TTS-to-PnP-Cards/releases

Its 200MB though I recommend just running the [TTStoPnp.py](TTStoPnp.py) file directly since 
A) you shouldn't run random exe files from the internet unless there's more than 11 people starring the repo
B) you sholdn't run random .py files from the internet unless there's more than 11 people starring the repo
C) but you can copy paste the .py file into the LLM of your choice to see if its doing something nefarious before running it.

## Usage

1. Click **Select Directory** or **Use Current Directory** to choose where your card sheet images are
2. For each image, enter the number of rows and columns in the card grid (typically 7 rows, 10 columns for TTS)
3. Use **Apply to All** to quickly set the same dimensions for all images
4. Leave dimensions as 0, 0 for any images you want to skip
5. Click **Separate Images**

Output files will be created in the same directory with names starting with `sep`.

## Notes

- Supported formats: PNG, JPG, JPEG
- Images with names starting with `sep` are automatically ignored (so you can re-run without processing previous output)
- The tool arranges cards into 3×3 grids for print-and-play layouts

## I'm scared about the exe file and am not sure how to run a .py file?

### 1. Check if Python is installed

Open a command prompt and run:

```
python --version
```

If you see a version number (e.g., `Python 3.12.0`), you're good. Skip to step 3.

If you get an error like `'python' is not recognized`, you need to install Python.

### 2. Install Python (if needed)

Download it from https://www.python.org/downloads/ and install (make sure to check the box that says "Add Python to PATH")

After installation, close and reopen your command prompt.

### 3. Install required packages (if needed)

```
pip install numpy Pillow
```

### 4. Run the tool

Navigate to the folder containing `TTStoPnp.py` and run:

```
python TTStoPnp.py
```
