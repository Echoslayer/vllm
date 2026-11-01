"""Compare real parser/connector paths without a model or HTTP server."""
import asyncio
import base64
import io
import json
from PIL import Image, ImageOps
from vllm.multimodal.media.base import MediaWithBytes
from vllm.multimodal.media.connector import MediaConnector
from vllm.multimodal.parse import MultiModalDataParser
from vllm.multimodal.utils import encode_image_url


def pixels(image):
    if isinstance(image, MediaWithBytes):
        image = image.media
    return image.size, image.mode, image.tobytes()


def parsed(image):
    return MultiModalDataParser().parse_mm_data({'image': image})['image'].get(0)


async def main():
    rows = []
    connector = MediaConnector()
    for source_format, mode in [('PNG', 'RGB'), ('PNG', 'RGBA'), ('JPEG', 'RGB')]:
        image = Image.new('RGB', (3, 2))
        image.putdata([(255, 0, 0), (0, 255, 0), (0, 0, 255),
                       (255, 255, 0), (255, 0, 255), (0, 255, 255)])
        image = image.convert(mode)
        image.getexif()[274] = 6
        buffer = io.BytesIO()
        image.save(buffer, format=source_format, exif=image.getexif())
        data = buffer.getvalue()
        source = Image.open(io.BytesIO(data))
        assert source.getexif()[274] == 6
        expected = parsed(source)
        assert pixels(expected)[0] == (2, 3)
        raw_url = 'data:image/' + source_format.lower() + ';base64,' + base64.b64encode(data).decode()
        original = connector.fetch_image(raw_url)
        assert pixels(parsed(original)) == pixels(expected)
        for output_format in ('PNG', 'JPEG'):
            encoded_url = encode_image_url(Image.open(io.BytesIO(data)), format=output_format)
            sync = parsed(connector.fetch_image(encoded_url))
            asynchronous = parsed(await connector.fetch_image_async(encoded_url))
            assert pixels(sync) == pixels(asynchronous)
            assert pixels(sync)[0] == (3, 2)
            normalized_url = encode_image_url(ImageOps.exif_transpose(Image.open(io.BytesIO(data))), format=output_format)
            normalized = parsed(connector.fetch_image(normalized_url))
            assert pixels(normalized)[0] == (2, 3)
            if output_format == 'PNG':
                assert pixels(normalized) == pixels(expected)
            rows.append({'source_format': source_format, 'mode': mode, 'output_format': output_format,
                         'direct_pil_size': list(pixels(expected)[0]),
                         'original_data_url_matches_pil': True,
                         'encoded_sync_size': list(pixels(sync)[0]),
                         'sync_async_pixels_match': True,
                         'pre_normalized_size': list(pixels(normalized)[0]),
                         'pre_normalized_pixels_match': pixels(normalized) == pixels(expected)})
    print(json.dumps(rows, indent=2))


asyncio.run(main())
