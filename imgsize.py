import imghdr
import struct


SIZE = {}


def size(fname):
    t = imghdr.what(fname)
    if t:
        with open(fname, 'rb') as fin:
            test = SIZE.get(t)
            if test:
                return dict(test(fin), type=t)


def size_jpeg(fin):
    soi = fin.read(2)
    assert soi == '\xff\xd8'
    while True:  # Find the SOFx block
        mkr, ll = struct.unpack('!2sH', fin.read(4))
        assert mkr[0] == '\xff'
        data = fin.read(ll - 2)
        if mkr[1] not in ('\xc0', '\xc1', '\xc2', '\xc3', '\xc5', '\xc6',
                          '\xc7', '\xc9', '\xca', '\xcb', '\xcd', '\xce',
                          '\xcf'):
            continue
        bps, height, width = struct.unpack('!cHH', data[:5])
        break
    return {
        'width': width,
        'height': height,
    }

SIZE['jpeg'] = size_jpeg


def size_png(fin):
    fin.read(8)  # Skip the Magick Numbers
    # First chunk MUST be IHDR
    clen, ctype = struct.unpack('!I4s', fin.read(8))
    assert ctype == 'IHDR'
    data = fin.read(clen)
    fin.read(4)  # CRC
    w, h, d, ct, comp, filt, ilace = struct.unpack('!IIccccc', data)
    return {
        'width': w,
        'height': h,
        'depth': ord(d),
    }

SIZE['png'] = size_png


def size_gif(fin):
    fin.read(6)  # Skip the Magick Numbers
    width, height = struct.unpack('<HH', fin.read(4))
    return {
        'width': width,
        'height': height,
    }

SIZE['gif'] = size_gif

# TIFF
# SGI RGB

# PBM
# PGM
# PPM
def size_pnm(fin):
    fin.read(2)  # Skip the Magick Numbers
    # Remember to skip lines starting with # after a newline
    width = height = 0
    # Then read width<s>height
    return {'width': width, 'height': height}

SIZE['pbm'] = size_pnm
SIZE['pgm'] = size_pnm
SIZE['ppm'] = size_pnm


# SUN Raster
# XBM
# BMP

if __name__ == '__main__':
    import sys

    for name in sys.argv[1:]:
        info = size(name)
        if not info:
            print("{}: Unknown".format(name))
        else:
            print("{}: {} {} x {} ({})".format(name,
                                               info['type'],
                                               info['width'],
                                               info['height'],
                                               info))
