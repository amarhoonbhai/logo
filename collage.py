from PIL import Image, ImageOps

def make_collage(images, grid_size, border_color="black", border_width=10, bg_color="white"):
    cols, rows = grid_size
    img_w, img_h = images[0].size

    total_width = cols * img_w + (cols + 1) * border_width
    total_height = rows * img_h + (rows + 1) * border_width

    collage = Image.new("RGB", (total_width, total_height), bg_color)

    for idx, img in enumerate(images):
        x = (idx % cols) * (img_w + border_width) + border_width
        y = (idx // cols) * (img_h + border_width) + border_width

        bordered = ImageOps.expand(img, border=border_width // 2, fill=border_color)
        collage.paste(bordered, (x, y))

    return collage