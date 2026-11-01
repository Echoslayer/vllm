import base64
import inspect
import io
import json
from PIL import Image
from vllm.multimodal.media.base import MediaWithBytes
from vllm.multimodal.media.image import ImageMediaIO
from vllm.multimodal.utils import encode_image_url

assert 'vllm-exif-experiment-20261102' in inspect.getfile(ImageMediaIO)
image=Image.new('RGBA',(3,2),(50,100,150,128))
image.getexif()[274]=6
for item in (image,MediaWithBytes(image,b'')):
    url=encode_image_url(item,image_mode=None)
    actual=Image.open(io.BytesIO(base64.b64decode(url.split(',',1)[1])))
    assert actual.size==(2,3) and actual.mode=='RGBA'
    assert actual.getpixel((0,0))==(50,100,150,128)
    assert actual.getexif().get(274,1)==1
assert image.size==(3,2) and image.getexif()[274]==6
print(json.dumps({'source_checkout_verified':True,'rgba_mode_none_preserved':True,'media_with_bytes_supported':True,'input_unchanged':True}))
