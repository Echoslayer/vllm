"""Check benchmark PIL/bytes conversion versus preserved source data URL."""
import base64
import io
import json
from PIL import Image
from vllm.benchmarks.datasets.datasets import process_image
from vllm.multimodal.media.connector import MediaConnector

image = Image.new('RGB', (3, 2), 'red')
image.getexif()[274] = 6
buffer = io.BytesIO()
image.save(buffer, format='JPEG', exif=image.getexif())
data = buffer.getvalue()
source_url = 'data:image/jpeg;base64,' + base64.b64encode(data).decode()
rows = []
for name, value in [('pil', Image.open(io.BytesIO(data))), ('bytes_dict', {'bytes': data}), ('data_url', source_url)]:
    output = process_image(value)['image_url']['url']
    loaded = MediaConnector().fetch_image(output)
    actual = loaded.media.size
    expected = (2, 3) if name == 'data_url' else (3, 2)
    assert actual == expected
    rows.append({'input': name, 'loaded_size': list(actual)})
print(json.dumps(rows, indent=2))
