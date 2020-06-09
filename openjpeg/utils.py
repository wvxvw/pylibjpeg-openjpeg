
from copy import deepcopy
from io import BytesIO, IOBase
from math import ceil

import _openjpeg


def _get_format(stream):
    """Return the JPEG 2000 format for the encoded data in `stream`.

    Parameters
    ----------
    stream : bytes or file-like
        A Python object containing the encoded JPEG 2000 data. If not
        :class:`bytes` then the object must have ``tell()``, ``seek()`` and
        ``read()`` methods.

    Returns
    -------
    int
        The format of the encoded data, one of:

        * ``0``: JPEG-2000 codestream
        * ``2``: JP2 file format

    Raises
    ------
    ValueError
        If no matching JPEG 2000 file format found for the data.
    """
    data = stream.read(20)
    stream.seek(0)
    #print(" ".join([f"{ii:02X}" for ii in data[:12]]))

    magic_numbers = {
        # JPEG 2000 codestream, has no header, .j2k, .jpc, .j2c
        b"\xff\x4f\xff\x51": 0,
        # JP2 and JP2 RFC3745, .jp2
        b"\x0d\x0a\x87\x0a": 2,
        b"\x00\x00\x00\x0c\x6a\x50\x20\x20\x0d\x0a\x87\x0a": 2,
        # JPT, .jpt - shrug
    }

    try:
        return magic_numbers[data[:4]]
    except KeyError:
        pass

    try:
        return magic_numbers[data[:12]]
    except KeyError:
        pass

    raise ValueError("No matching JPEG 2000 format found")


def get_openjpeg_version():
    """Return the openjpeg version as tuple of int."""
    version = _openjpeg.get_version().decode("ascii").split(".")
    return tuple([int(ii) for ii in version])


def decode(stream, j2k_format=None, reshape=True):
    """Return the decoded JPEG2000 data from `stream` as a
    :class:`numpy.ndarray`.

    Parameters
    ----------
    stream : bytes or file-like
        A Python object containing the encoded JPEG 2000 data. If not
        :class:`bytes` then the object must have ``tell()``, ``seek()`` and
        ``read()`` methods.
    j2k_format : int, optional
        The JPEG 2000 format to use for decoding, one of:

        * ``0``: JPEG-2000 codestream (such as from DICOM *Pixel Data*)
        * ``1``: JPT-stream (JPEG 2000, JPIP)
        * ``2``: JP2 file format
    reshape : bool, optional
        Reshape and re-view the output array so it matches the image data
        (default), otherwise return a 1D array of ``np.uint8``.

    Returns
    -------
    numpy.ndarray
        An array of containing the decoded image data.

    Raises
    ------
    RuntimeError
        If the decoding failed.
    """
    if isinstance(stream, (bytes, bytearray)):
        stream = BytesIO(stream)

    required_methods = ["read", "tell", "seek"]
    if not all([hasattr(stream, meth) for meth in required_methods]):
        raise TypeError(
            "The Python object containing the encoded JPEG 2000 data must "
            "have read(), tell() and seek() methods."
        )

    if j2k_format is None:
        j2k_format = _get_format(stream)

    assert isinstance(j2k_format, int)

    arr = _openjpeg.decode(stream, j2k_format)
    if not reshape:
        return arr

    meta = get_parameters(stream, j2k_format)
    bpp = ceil(meta["precision"] / 8)

    dtype = f"uint{8 * bpp}" if not meta["is_signed"] else f"int{8 * bpp}"
    arr = arr.view(dtype)

    shape = [meta["rows"], meta["columns"]]
    if meta["nr_components"] > 1:
        shape.append(meta["nr_components"])

    return arr.reshape(*shape)


def get_parameters(stream, j2k_format=None):
    """Return a :class:`dict` containing the JPEG2000 image parameters.

    Parameters
    ----------
    stream : bytes or file-like
        A Python object containing the encoded JPEG 2000 data. If not
        :class:`bytes` then the object must have ``tell()``, ``seek()`` and
        ``read()`` methods.
    j2k_format : int, optional
        The JPEG 2000 format to use for decoding, one of:

        * ``0``: JPEG-2000 codestream (such as from DICOM *Pixel Data*)
        * ``1``: JPT-stream (JPEG 2000, JPIP)
        * ``2``: JP2 file format

    Returns
    -------
    dict
        A :class:`dict` containing the J2K image parameters:
        ``{'columns': int, 'rows': int, 'colourspace': str,
        'nr_components: int, 'precision': int, `is_signed`: bool}``. Possible
        colour spaces are "unknown", "unspecified", "sRGB", "monochrome",
        "YUV", "e-YCC" and "CYMK".

    Raises
    ------
    RuntimeError
        If reading the image parameters failed.
    """
    if isinstance(stream, (bytes, bytearray)):
        stream = BytesIO(stream)

    required_methods = ["read", "tell", "seek"]
    if not all([hasattr(stream, func) for func in required_methods]):
        raise TypeError(
            "The Python object containing the encoded JPEG 2000 data must "
            "have read(), tell() and seek() methods."
        )

    if j2k_format is None:
        j2k_format = _get_format(stream)

    assert isinstance(j2k_format, int)

    return _openjpeg.get_parameters(stream, j2k_format)
