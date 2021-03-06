#!/bin/python
# vim: set fileencoding=utf-8

"""
Join (with blending) several screenshots into one big file
and (optionally) splitting it again in small tiles.
"""

import os
import os.path
import sys
import shutil

path = "./"
image_out = "out.png"
# os.popen("rm {file}".format(file=image_out))

settings = {
    1024: {
        "dim": [1024, 768],
        "overlap": [205, 39],
    },
    1800: {
        "dim": [1800, 1000],
        "overlap": [177, 188],
        # "overlap": [17, 483],  # pitch=15.0,
    },
}

grid = [9, int(64/9)]

out_dim = []


# Stage 0
def preblend_input(dim, src, mask_file, dst):
    if not os.path.exists(mask_file):
        grad_height = 160  # found by try&error
        sMask = "convert -size {0}x{1} gradient:'rgb(220,220,220)'-white -size {0}x{2} " \
            "xc:white -append {3}".format(
                dim[0],
                grad_height,
                dim[1]-grad_height,
                mask_file,
            )
        os.popen(sMask)

    s = " convert {0} {1} -compose DivideSrc -composite {result}".format(
        src,
        mask_file,
        result=dst,
    )

    print s
    os.popen(s)


# Stage 1, horizontal merge
def overlap_h(dim, overlap, images, out):
    s = "convert -size {1}x{0} xc:white -size {2}x{1} gradient: -append " \
        "-rotate 90 {3} ".format(
            dim[0]-overlap[0],
            overlap[0],
            dim[1],  # len(images) * dim[0] - (len(images)-1) * overlap[0],
            images[0]
        )

    for i in range(1, len(images)):
        s += "\( {0} -clone 0 -compose CopyOpacity +matte "\
            "-composite -repage +{1}+0 \) ".format(
                images[i],
                i*(dim[0]-overlap[0]))

    s += "-delete 0 -compose Over -mosaic {0}".format(out)

    print s
    os.popen(s)


# Stage 2, vertical merge
def overlap_v(dim, overlap, images, out):
    s = "convert -rotate 180 -size {2}x{1} gradient: -size {2}x{0} xc:white -append " \
        " {3} -rotate 0 -repage +0+{4} ".format(
            dim[1]-overlap[1],
            overlap[1],
            out_dim[0],
            images[0],
            0*(len(images)-1)*(dim[1]-overlap[1])
        )

    for i in range(1, len(images)):
        s += "\( {0} -clone 0 -compose CopyOpacity +matte "\
            "-composite -repage +0+{1} \) ".format(
                images[i],
                i*(dim[1]-overlap[1]))

    s += "-delete 0 -compose Over -mosaic {0}".format(out)
    #  s += "-compose Over -mosaic {0}".format(out)

    print s
    os.popen(s)


def read_image_dimension(filename):
    """ Use ImageMagick tool to detect dimensions."""
    cmd = "identify {0}".format(filename)
    result = os.popen(cmd).read()
    # Example string
    # 'out.png PNG 7576x5142 7576x5142+0+0 8-bit DirectClass 46.87MB [...]\n'
    sr = result.split(" ")[2].split("x")
    return map(int, sr)

# Stage 3


def create_levels(filename):
    """ Recreate level/X subdirectories. """

    """ Level goes from  0 to max_level, but folder names are shifted for leaflet
    Level |    Dimensions   | Num tiles                 | Folder
        0 |       1x1       | 1         (dummy level)   | -max_level
        1 |     256x256     | 1                         | -max_level + 1
        l | 2^(l+8)x2^(l+8) | 2^(2*l)                   | -max_level + l

    If base image is no multiple of 2^(max_level+8), some thin
    border images will be added.
    """
    tile_dim = [256, 256]

    out_dim = read_image_dimension(filename)
    print("File dimensions:" + str(out_dim))

    # Get maximal level
    import math
    m = max([1, min(out_dim)/256.0])
    max_level = int(math.ceil(math.log(m, 2)))
    print("Maximal level: %d" % (max_level))

    # Remove old images
    try:
        shutil.rmtree("levels")
    except OSError:
        pass
    os.mkdir("levels")

    # 1. Highest resolution tilling (no rescaling)
    os.mkdir("./levels/{0}".format(0))
    s = "convert {0} -crop {1}x{2} +repage levels/{3}/tile_%d.jpg".format(
        path+image_out,
        tile_dim[0], tile_dim[1],
        0,
    )
    print(s)
    os.popen(s)

    # 2. Sublevel
    for level in range(0, max_level, 1):
        pot = 2**(max_level-level)
        resize_factor = 100.0/pot
        os.mkdir("./levels/{0}".format(level-max_level))
        s = "convert {0} -resize {4}%x -crop {1}x{2} +repage " \
            "levels/{3}/tile_%d.jpg".format(
                path+image_out,
                # path+"Civ4ScreenShot0000.JPG",
                tile_dim[0], tile_dim[1],
                level - max_level,
                resize_factor,
            )
        print("Level %i, Resize %%: %f" % (level, resize_factor,))
        os.popen(s)


def main(args):
    # Handle args
    grid[0] = int(args.get(1, grid[0]))  # Width in number of images
    grid[1] = int(args.get(2, grid[1]))  # Height in number of images
    num_start = int(args.get(3, 0))  # Index of first image.
    steps = int(args.get(4, 0))  # Bitflags for converting stages
    setting_id = int(args.get(5, 1800))

    # Setup
    dim = settings[setting_id]["dim"]
    overlap = settings[setting_id]["overlap"]
    images_in = []

    for i in range(grid[0]*grid[1]):
        images_in.append("Civ4ScreenShot%04d.JPG" % (num_start+i))

    for i in range(2):
        out_dim.append(grid[i] * dim[i] - (grid[i]-1) * overlap[i])

    outs_h = []
    preblend = bool(steps & 0x1)
    horizontal = bool(steps & 0x2)
    vertical = bool(steps & 0x4)
    tiling = bool(steps & 0x8)
    transparent_dummy = bool(steps & 0x10)

    print "Estimated dimension: %ix%i" % (out_dim[0], out_dim[1])

    # Gen preblend filenames
    images_blend = []
    for img in images_in:
        limg = img.split(".")
        limg.append("png")  # limg[-1])
        limg[-2] = "blend"
        images_blend.append(".".join(limg))

    # Processing
    # Stage 0
    if preblend:
        mask_file = "tmp_mask.mpc"
        # trigger re-creation of mask
        os.popen("rm {file}".format(file=mask_file))
        for i in range(len(images_in)):
            if not os.path.isfile(images_blend[i]):
                print("Blend %s" % (images_in[i]))
                preblend_input(dim, images_in[i], mask_file, images_blend[i])
            else:
                print("%s already blended." % (images_blend[i]))

        # Continue with preblend images.
        images_in = images_blend

    # Stage 1
    for j in range(grid[1]):
        outs_h.append(path+"out%02d.png" % (j))
        if horizontal:
            overlap_h(dim, overlap, images_in[j*grid[0]:(j+1)*grid[0]],
                      outs_h[j])

    # Stage 2
    if vertical:
        outs_h.reverse()
        overlap_v(dim, overlap, outs_h, path+image_out)

    # Stage 3
    if tiling:
        create_levels(path+image_out)

    # Optional (dummy file for leaflet map)
    if transparent_dummy:
        # Transparent image
        os.popen(
            "convert -size 256x256 xc:transparent ./levels/transparent.png")

if __name__ == "__main__":
    args = dict(zip(range(len(sys.argv)), sys.argv))

    if args.get(1) in ["-h", "--help"]:
        print "Usage: python {0} {1} {2} {3} {4} {5}".format(
            args.get(0),
            "{Width}", "{Height}",
            "[Index of first]",
            "[Flags]",
            "[Setting id]",
        )
        print """
        - Width and Height are the number of Screenshots for each direction.
          Depends from the map size.
        - Index (default=0) is the lowest number in Civ4ScreenShotXXXX.JPG.
        - Flags (default=31 / invoke all converting steps) control the
                different converting steps.
            1: Preblending to correct luminance (reduce banding).
            2: Join images horizontal
            4: Join images vertical => Produce one big image
            8: Create Tiles => Split big image into 256x256 tiles
               at different zooming levels.
        - Setting id (default=1800) Select geometry definition. Default one
          matches screenshots with a resolution of 1800x1000.
          Use CivilizationIV.ini to set the game on this resolution.
              """

    else:
        main(args)
