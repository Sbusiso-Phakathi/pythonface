from PIL import Image
import io

def convert_image_to_rgb(image_data):
    image = Image.open(io.BytesIO(image_data))
    if image.mode == "RGBA":
        image = image.convert("RGB")
    return image
