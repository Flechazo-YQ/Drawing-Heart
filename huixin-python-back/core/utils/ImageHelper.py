import re, base64, logging

from typing import Optional

class ImageHelper:

    @staticmethod
    def decodeBase64Image(imageDataBase64: str) -> Optional[bytes]:
        try:
            if ("base64" in imageDataBase64):
                (_, imageDataBase64) = imageDataBase64.split("base64,", 1)

            imageDataBase64 = re.sub(r'[^A-Za-z0-9+/=]', '', imageDataBase64)
            missingPadding = len(imageDataBase64) % 4

            if (missingPadding):
                imageDataBase64 += "=" * (4 - missingPadding)

            return base64.b64decode(imageDataBase64)
        except Exception as e:
            logging.error(f"❌ Base64解码失败: { str(e) }")
            return None
