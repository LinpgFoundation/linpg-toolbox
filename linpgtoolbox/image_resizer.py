import os
import re
import sys
from typing import Any


class ImageResizer:
    @classmethod
    def resize(cls, image_path: str, size: str, output: str | None = None) -> None:
        try:
            from PIL import Image
        except ImportError:
            print(
                "Pillow is not installed. Please install it using 'pip install Pillow'"
            )
            sys.exit(1)

        # if input is a directory, process all images in it
        if os.path.isdir(image_path):
            # validate output is a directory if provided
            if output and os.path.isfile(output):
                print("Error: Output must be a directory when input is a directory.")
                return

            # create output directory if it doesn't exist
            if output and not os.path.exists(output):
                os.makedirs(output)

            # common image extensions
            extensions: set[str] = {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
                ".bmp",
                ".gif",
                ".tiff",
            }

            for file_name in os.listdir(image_path):
                if os.path.splitext(file_name)[1].lower() in extensions:
                    cls.resize(
                        os.path.join(image_path, file_name),
                        size,
                        os.path.join(output, file_name) if output else None,
                    )
            return

        # validate image file exists
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # parse size string
        dim_match = re.fullmatch(r"(\d+)x(\d+)", size)
        pct_match = re.fullmatch(r"(\d+)%", size)
        width_match = re.fullmatch(r"(\d+)x", size)
        height_match = re.fullmatch(r"x(\d+)", size)

        with Image.open(image_path) as img:
            if dim_match:
                width, height = int(dim_match.group(1)), int(dim_match.group(2))
                suffix = f"_{width}x{height}"
            elif pct_match:
                percent = int(pct_match.group(1))
                width = round(img.width * percent / 100)
                height = round(img.height * percent / 100)
                suffix = f"_{percent}p"
            elif width_match:
                width = int(width_match.group(1))
                height = round(img.height * width / img.width)
                suffix = f"_{width}x{height}"
            elif height_match:
                height = int(height_match.group(1))
                width = round(img.width * height / img.height)
                suffix = f"_{width}x{height}"
            else:
                raise ValueError(
                    f"Invalid size format: '{size}'. Use WxH, N%, Wx, or xH"
                )

            if (
                (width_match and width == img.width)
                or (height_match and height == img.height)
                or (width == img.width and height == img.height)
            ):
                print(
                    f"Image size is already {img.width}x{img.height}. Skipping resize."
                )
                return

            resized = img.resize((width, height), Image.Resampling.LANCZOS)

            # determine output path
            if output is None:
                name, ext = os.path.splitext(image_path)
                output = f"{name}{suffix}{ext}"

            # Save with highest quality settings
            save_kwargs: dict[str, Any] = {}
            if output.lower().endswith((".jpg", ".jpeg")):
                save_kwargs.update({"quality": 100, "subsampling": 0})
            elif output.lower().endswith(".webp"):
                save_kwargs.update({"quality": 100, "lossless": True})

            resized.save(output, **save_kwargs)
            print(f"Saved resized image to: {output}")
