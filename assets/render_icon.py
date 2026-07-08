# /// script
# requires-python = ">=3.11"
# dependencies = ["pyobjc-framework-Cocoa"]
# ///
"""Render Awake's app icon: the ☕ emoji on a soft rounded background.

Draws a 1024×1024 master PNG offscreen with AppKit/CoreText (the reliable way
to rasterize Apple's color emoji), written next to this script as master.png.
Build the .icns from it with build_icns.sh.
"""

import os

from AppKit import (
    NSAttributedString,
    NSBezierPath,
    NSBitmapImageRep,
    NSColor,
    NSFont,
    NSGradient,
    NSGraphicsContext,
)
from Foundation import NSMakePoint, NSMakeRect

SIZE = 1024
NS_FONT_ATTR = "NSFont"
NS_PNG_FILE_TYPE = 4  # NSBitmapImageFileTypePNG
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "master.png")


def main() -> None:
    rep = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_(
        None, SIZE, SIZE, 8, 4, True, False, "NSCalibratedRGBColorSpace", 0, 0
    )
    ctx = NSGraphicsContext.graphicsContextWithBitmapImageRep_(rep)
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.setCurrentContext_(ctx)

    # Rounded-rect background (soft off-white gradient) with a transparent margin,
    # matching the macOS icon grid.
    margin = 96.0
    radius = 224.0
    rect = NSMakeRect(margin, margin, SIZE - 2 * margin, SIZE - 2 * margin)
    path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(rect, radius, radius)
    top = NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 1.0, 1.0, 1.0)
    bottom = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.90, 0.91, 0.93, 1.0)
    NSGradient.alloc().initWithStartingColor_endingColor_(top, bottom).drawInBezierPath_angle_(
        path, -90.0
    )

    # Centered ☕ emoji.
    emoji = "☕"
    font = NSFont.fontWithName_size_("Apple Color Emoji", 560.0) or NSFont.systemFontOfSize_(560.0)
    attributed = NSAttributedString.alloc().initWithString_attributes_(emoji, {NS_FONT_ATTR: font})
    size = attributed.size()
    point = NSMakePoint((SIZE - size.width) / 2.0, (SIZE - size.height) / 2.0)
    attributed.drawAtPoint_(point)

    NSGraphicsContext.restoreGraphicsState()

    png = rep.representationUsingType_properties_(NS_PNG_FILE_TYPE, {})
    png.writeToFile_atomically_(OUT, True)
    print(f"wrote {OUT} ({png.length()} bytes)")


if __name__ == "__main__":
    main()
