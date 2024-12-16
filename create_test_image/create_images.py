#! /usr/bin/venv python3

"""
This script will create test images for supported format with one bright pixel in the center.
"""

import argparse
import OpenEXR
import os
from PIL import Image
import numpy as np
import Imath


def create_image(size, image_format):
    image = np.zeros((size, size, 3), dtype=np.uint8)
    image[size // 2, size // 2] = [255, 255, 255]
    return image


def save_image(image, output_image, image_format):
    if image_format.lower() == "exr":
        save_exr(image, output_image)
    else:
        img = Image.fromarray(image, "RGB")
        img.save(output_image)


def save_exr(image, output_image):
    height, width, channels = image.shape
    header = OpenEXR.Header(width, height)
    header['channels'] = {'R': Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT)),
                          'G': Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT)),
                          'B': Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))}
    exr = OpenEXR.OutputFile(output_image, header)
    r = (image[:, :, 0].astype(np.float32) / 255.0).tobytes()
    g = (image[:, :, 1].astype(np.float32) / 255.0).tobytes()
    b = (image[:, :, 2].astype(np.float32) / 255.0).tobytes()
    exr.writePixels({'R': r, 'G': g, 'B': b})
    exr.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Create test images")
    parser.add_argument("-o", "--output-folder", type=str, default=".", help="Output folder")
    parser.add_argument("-s", "--size", type=int, default=256, help="Size of the image")
    parser.add_argument("-f", "--format", type=str, default="exr", help="Image format")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    image_format = args.format
    size = args.size
    output_image = os.path.join(args.output_folder, f"test_image.{image_format}")
    print(f"Creating image {output_image}")

    image = create_image(size, image_format)
    save_image(image, output_image, image_format)

if __name__ == "__main__":
    main()