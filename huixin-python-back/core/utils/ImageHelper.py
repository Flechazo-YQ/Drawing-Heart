import re, base64, logging, os

from typing import Optional, Final

class ImageHelper:
    MIME_TYPE_CONFIG: Final[dict[str, str]] = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    # 图像Base64解码
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
        
    # 将图片文件转换为 data URL
    @classmethod
    def imageToDataUrl(cls, filePath: str):

        # 将图片文件转换为 data URL
        try:
            extension = os.path.splitext(filePath)[1].lower()
            mimeType = cls.MIME_TYPE_CONFIG.get(extension)

            # 读取文件并转换为 base64
            with open(filePath, "rb") as imageFile:
                encodedImage = base64.b64encode(imageFile.read()).decode("utf-8")

            # 返回完整的 data URL
            return f"data:{ mimeType };base64,{ encodedImage }"

        except Exception as e:
            logging.error(f"❌ 图片转换失败: { str(e) }")
            return None
