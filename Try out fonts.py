from PIL import Image, ImageDraw, ImageFont
import matplotlib.font_manager as fm

# Collect system font paths
font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')

# Parameters
sample_text = "The quick brown fox jumps over 123"
font_size = 32
padding = 10
line_height = font_size + 20
cols = 2   # number of columns in the output image

# Create canvas big enough for all fonts
rows = (len(font_paths) + cols - 1) // cols
img_width = 1000
img_height = rows * line_height
img = Image.new("RGB", (img_width, img_height), "white")
draw = ImageDraw.Draw(img)

for i, font_path in enumerate(font_paths):
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        continue  # skip broken fonts

    col = i % cols
    row = i // cols
    x = col * (img_width // cols) + padding
    y = row * line_height + padding

    # font name
    font_name = fm.FontProperties(fname=font_path).get_name()
    draw.text((x, y), f"{font_name}:", fill="black", font=ImageFont.load_default())

    # sample text
    draw.text((x + 200, y), sample_text, fill="black", font=font)

# Save result
img.save("fonts_overview.png")
print("✅ Saved fonts_overview.png")
