"""Compare encoding policies with real vLLM and mistral-common decoders."""
import base64
import io
import json
from importlib.metadata import version
from PIL import Image, ImageOps
from mistral_common.protocol.instruct.messages import ImageURLChunk
from mistral_common.tokens.tokenizers.image import image_from_chunk
from vllm.multimodal.media.connector import MediaConnector
from vllm.multimodal.utils import encode_image_url

source = Image.new('RGB', (3, 2))
source.putdata([(255, 0, 0), (0, 255, 0), (0, 0, 255),
                (255, 255, 0), (255, 0, 255), (0, 255, 255)])
source.getexif()[274] = 6
buffer = io.BytesIO()
source.save(buffer, 'PNG', exif=source.getexif())
data = buffer.getvalue()
source_url = 'data:image/png;base64,' + base64.b64encode(data).decode()
urls = {'preserve_original_bytes': source_url,
        'current_helper': encode_image_url(Image.open(io.BytesIO(data))),
        'normalize_before_helper': encode_image_url(ImageOps.exif_transpose(Image.open(io.BytesIO(data))))}
rows = []
for policy, url in urls.items():
    mistral = image_from_chunk(ImageURLChunk(image_url=url))
    vllm = MediaConnector().fetch_image(url).media
    expected_mistral = (2, 3) if policy == 'normalize_before_helper' else (3, 2)
    expected_vllm = (3, 2) if policy == 'current_helper' else (2, 3)
    assert mistral.size == expected_mistral and vllm.size == expected_vllm
    rows.append({'policy': policy, 'mistral_size': list(mistral.size),
                 'vllm_size': list(vllm.size),
                 'pixels_equal': mistral.tobytes() == vllm.tobytes() and mistral.size == vllm.size})
print(json.dumps({'mistral_common': version('mistral-common'), 'pillow': version('pillow'), 'results': rows}, indent=2))
