import io
import unittest
import mock
import filetype

from willow.image import (
    Image, JPEGImageFile, PNGImageFile, GIFImageFile, UnrecognisedImageFormatError,
    BMPImageFile, TIFFImageFile
)


class TestOpenImage(unittest.TestCase):
    """
    Tests that Image.open responds correctly to different image headers.

    Note that Image.open is not responsible for verifying image contents so
    these tests do not require valid images.
    """
    def test_opens_jpeg(self):
        f = io.BytesIO()
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00')
        f.seek(0)

        image = Image.open(f)
        self.assertIsInstance(image, JPEGImageFile)
        self.assertEqual(image.format_name, 'jpeg')
        self.assertEqual(image.original_format, 'jpeg')

    def test_opens_png(self):
        f = io.BytesIO()
        f.write(b'\x89PNG\x0d\x0a\x1a\x0a')
        f.seek(0)

        image = Image.open(f)
        self.assertIsInstance(image, PNGImageFile)
        self.assertEqual(image.format_name, 'png')
        self.assertEqual(image.original_format, 'png')

    def test_opens_gif(self):
        f = io.BytesIO()
        f.write(b'GIF89a')
        f.seek(0)

        image = Image.open(f)
        self.assertIsInstance(image, GIFImageFile)
        self.assertEqual(image.format_name, 'gif')
        self.assertEqual(image.original_format, 'gif')

    def test_raises_error_on_invalid_header(self):
        f = io.BytesIO()
        f.write(b'Not an image')
        f.seek(0)

        with self.assertRaises(UnrecognisedImageFormatError) as e:
            Image.open(f)


class TestImageFormats(unittest.TestCase):
    """
    Tests image formats that are not well covered by the remaining tests.
    """

    def test_bmp(self):
        with open('tests/images/sails.bmp', 'rb') as f:
            image = Image.open(f)
            width, height = image.get_size()

        self.assertIsInstance(image, BMPImageFile)
        self.assertEqual(width, 768)
        self.assertEqual(height, 512)

    def test_tiff(self):
        with open('tests/images/cameraman.tif', 'rb') as f:
            image = Image.open(f)
            width, height = image.get_size()

        self.assertIsInstance(image, TIFFImageFile)
        self.assertEqual(width, 256)
        self.assertEqual(height, 256)


class TestSaveImage(unittest.TestCase):
    """
    Image.save must work out the name of the underlying operation based on the
    format name and call it. It must not however, allow an invalid image format
    name to be passed.
    """
    def test_save_as_jpeg(self):
        image = Image()
        image.save_as_jpeg = mock.MagicMock()

        image.save("jpeg", "outfile")
        image.save_as_jpeg.assert_called_with("outfile")

    def test_save_as_foo(self):
        image = Image()
        image.save_as_jpeg = mock.MagicMock()

        with self.assertRaises(ValueError):
            image.save("foo", "outfile")

        self.assertFalse(image.save_as_jpeg.mock_calls)


class TestImghdrJPEGPatch(unittest.TestCase):
    def test_detects_photoshop3_jpeg(self):
        f = io.BytesIO()
        f.write(b'\xff\xd8\xff\xed\x00,Photoshop 3.0\x00')
        f.seek(0)

        image_format = filetype.guess_extension(f)

        self.assertEqual(image_format, 'jpg')

    def test_junk(self):
        f = io.BytesIO()
        f.write(b'Not an image')
        f.seek(0)

        image_format = filetype.guess_extension(f)

        self.assertIsNone(image_format)
