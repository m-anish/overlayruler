#!/usr/bin/python
# coding: utf-8

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import exiftool


def calculate_ruler(filename):
    # Use exiftool to extract EXIF and MakerNotes tags from the input image
    with exiftool.ExifTool() as et:
        metadata = et.get_metadata_batch([filename])

    # Focus Distance in mm
    Do = float(metadata[0]['MakerNotes:FocusDistance']) * 1000

    # Focal length in mm
    F = float(metadata[0]['EXIF:FocalLength'])

    # Sensor height: Compute from the ratio between Focal Length and
    # 35mm-Equivalent Focal Length tags in mm
    Hs = 24 * float(metadata[0]['EXIF:FocalLength']) /         float(metadata[0]['EXIF:FocalLengthIn35mmFormat'])

    # Vertical height of the frame in mm
    Hr = ((Do * Hs) / F)

    return Hr


def overlay_ruler(filename):
    # Open and check file extension
    image = Image.open(filename, 'r')
    if not (filename.endswith('.JPG') or filename.endswith('.jpg')):
        raise ValueError(
            "Incorrect file extension. This utility only works with .jpg or .JPG images")

    pixel_size = image.height

    try:
        actual_size = calculate_ruler(filename)
    except KeyError:
        print("Input image %s doesn't contain the EXIF data required to compute scale." % filename)
        raise

    # Start building a ruler
    ticks = 10
    tick_width = int(pixel_size/100)
    tick_length = image.width/20
    tick_skip = pixel_size/ticks
    tick_scale_mm = actual_size/ticks

    # Overlay the ruler on the image
    draw = ImageDraw.Draw(image)
    draw.line((0, 0, 0, pixel_size), fill=0, width=tick_width)

    font = ImageFont.truetype("FreeSans.ttf", int(pixel_size/15))
    draw.text((tick_width*2, tick_width*2), "1 division = %d mm" %
              tick_scale_mm, (0, 0, 0), font=font)

    for i in range(0, ticks + 1):
        draw.line((0, i*tick_skip, tick_length, i*tick_skip),
                  fill=0, width=tick_width)

    return image


import re

file = "/home/anish/_DSC0358.JPG"

file_regex = re.compile(r"(.*\.)(jpg)", re.IGNORECASE)
output_filename = re.sub(file_regex, r"\1overlay.\2", file)

overlay_ruler(file).save(output_filename, 'JPEG', quality=90)

