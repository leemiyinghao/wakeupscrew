from wand.image import Image
from wand.api import library
from ctypes import c_void_p, c_size_t
library.MagickSetCompressionQuality.argtypes = [c_void_p, c_size_t]

def HEICEncode(otherBlob):
    other = Image(blob=otherBlob)
    other.format = 'heic'
    return other.make_blob()

def HEICDecode(heicBlob, _format='jpg'):
    heic = Image(blob=heicBlob)
    heic.format = _format
    if _format in ['jpg', 'jpeg']:
        library.MagickSetCompressionQuality(heic.wand, 100)
    return heic.make_blob()