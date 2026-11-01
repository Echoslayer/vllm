"""Small, valid PNG inputs; run with the installed vLLM environment."""
import base64
import io
import json
from PIL import Image, ImageOps
from vllm.multimodal.media.image import ImageMediaIO
from vllm.multimodal.utils import encode_image_base64


def same(a, b):
    return (a.size, a.mode, a.tobytes()) == (b.size, b.mode, b.tobytes())


rows = []
for mode in ('RGB', 'RGBA', 'LA'):
    for orientation in range(1, 9):
        image = Image.new('RGB', (3, 2))
        image.putdata([(255, 0, 0), (0, 255, 0), (0, 0, 255),
                       (255, 255, 0), (255, 0, 255), (0, 255, 255)])
        image = image.convert(mode)
        image.getexif()[274] = orientation
        buf = io.BytesIO()
        image.save(buf, format='PNG', exif=image.getexif())
        original = Image.open(io.BytesIO(buf.getvalue()))
        assert original.getexif()[274] == orientation
        normalized = ImageOps.exif_transpose(original)
        expected = normalized.convert('RGB')
        assert expected.size == ((2, 3) if orientation >= 5 else (3, 2))
        direct = ImageMediaIO().load_bytes(buf.getvalue()).media
        kept = ImageMediaIO(image_mode=None).load_bytes(buf.getvalue()).media
        payload = encode_image_base64(original)
        encoded_file = Image.open(io.BytesIO(base64.b64decode(payload)))
        encoded = ImageMediaIO().load_base64('image/png', payload).media
        pre_normalized = ImageMediaIO().load_base64(
            'image/png', encode_image_base64(normalized)).media
        assert same(direct, expected) and same(kept, normalized)
        assert same(pre_normalized, expected)
        rows.append({'mode': mode, 'orientation': orientation,
                     'load_bytes_matches': True, 'preserve_mode_matches': True,
                     'encode_roundtrip_matches': same(encoded, expected),
                     'encode_after_normalization_matches': True,
                     'encoded_exif_orientation': encoded_file.getexif().get(274),
                     'expected_size': list(expected.size), 'encoded_size': list(encoded.size)})

transparency = []
for mode in ('RGBA', 'LA', 'P', 'L', 'RGB'):
    source = Image.new(mode, (3, 1))
    if mode == 'RGBA':
        source.putdata([(100, 50, 200, a) for a in (0, 128, 255)])
    elif mode == 'LA':
        source.putdata([(100, a) for a in (0, 128, 255)])
    elif mode == 'P':
        source.putpalette([100, 50, 200] * 256)
        source.putdata([0, 1, 2])
        source.info['transparency'] = bytes([0, 128, 255])
    elif mode == 'L':
        source.putdata([0, 100, 200])
        source.info['transparency'] = 0
    else:
        source.putdata([(0, 0, 0), (100, 50, 200), (255, 255, 255)])
        source.info['transparency'] = (0, 0, 0)
    buffer = io.BytesIO()
    source.save(buffer, format='PNG')
    data = buffer.getvalue()
    loaded = Image.open(io.BytesIO(data))
    preserved = ImageMediaIO(image_mode=None).load_bytes(data).media
    assert same(preserved, loaded)
    assert same(preserved.convert('RGBA'), loaded.convert('RGBA'))
    for bg in ((255, 255, 255), (10, 20, 30)):
        expected = Image.alpha_composite(Image.new('RGBA', source.size, bg + (255,)),
                                         loaded.convert('RGBA')).convert('RGB')
        actual = ImageMediaIO(rgba_background_color=bg).load_bytes(data).media
        assert same(actual, expected)
        transparency.append({'mode': mode, 'background': list(bg), 'matches': True})
print(json.dumps({'orientation': rows, 'transparency': transparency}, indent=2))
