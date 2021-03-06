# coding: utf-8
# overlayruler <http://github.com/m-anish/overlayruler>
# Copyright 2018 Anish Mangal

# This file is part of overlayruler.
#
# overlayruler is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the licence.
#   
# overlayruler is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING for more details.

import os
import exiftool
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def calculate_ruler(filename):
    # Use exiftool to extract EXIF and MakerNotes tags from the input image
    with exiftool.ExifTool() as et:
        metadata = et.get_metadata_batch([filename])

    # Focus Distance in mm
    focus_distance = float(metadata[0]['MakerNotes:FocusDistance']) * 1000

    # Focal length in mm
    focal_length = float(metadata[0]['EXIF:FocalLength'])

    # Sensor height: Compute from the ratio between Focal Length and
    # 35mm-Equivalent Focal Length tags in mm
    sensor_height = 24 * float(metadata[0]['EXIF:FocalLength']) /         float(metadata[0]['EXIF:FocalLengthIn35mmFormat'])

    # Vertical height of the frame in mm
    # See: https://photo.stackexchange.com/questions/12434/how-do-i-calculate-the-distance-of-an-object-in-a-photo
    frame_height = ((focus_distance * sensor_height) / focal_length)

    return frame_height


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

    here = os.path.abspath(os.path.dirname(__file__))
    font = ImageFont.truetype(os.path.join(here, 'fonts/FreeSans.ttf'), int(pixel_size/15))
    draw.text((tick_width*2, tick_width*2), "1 division = %d mm" %
              tick_scale_mm, (0, 0, 0), font=font)

    for tick in range(0, ticks + 1):
        draw.line((0, tick*tick_skip, tick_length, tick*tick_skip),
                  fill=0, width=tick_width)

    return image, image.info['exif']


import re

file = "/home/anish/_DSC0358.JPG"

file_regex = re.compile(r"(.*\.)(jpg)", re.IGNORECASE)
output_filename = re.sub(file_regex, r"\1overlay.\2", file)

image, exif = overlay_ruler(file)
image.save(output_filename, 'JPEG', quality=90, exif=exif)

