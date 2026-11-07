from pathlib import Path
from PIL import Image, ImageOps

def preprocess_image(
        input_path:Path,
        output_directory:Path,
)->Path:
    output_directory.mkdir(parents=True,exist_ok=True)
    output_path=output_directory/f"{input_path.stem}_processed.jpg"

    with Image.open(input_path) as image:
        corrected_image=ImageOps.exif_transpose(image)
        rbg_image=corrected_image.convert("RGB")
        rbg_image.save(
            output_path,
            format="JPEG",
            quality=95,
            optimize=True
        )
    return output_path
