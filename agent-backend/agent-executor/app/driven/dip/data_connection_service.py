from base64 import b64decode
from typing import Any, Dict, Optional

import aiohttp
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from app.common.config import Config
from app.common.stand_log import StandLogger


class DpDataSourceService(object):
    """数据源管理服务调用"""

    def __init__(self, headers: dict = None):
        self._basic_url = "http://{}:{}".format(
            Config.services.data_connection.host, Config.services.data_connection.port
        )
        self.headers = headers or {}

    async def get_datasource_by_id(self, ds_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取单个数据源信息

        Args:
            ds_id: 数据源ID

        Returns:
            数据源信息，如果不存在返回None
        """
        api = f"{self._basic_url}/api/internal/data-connection/v1/datasource/{ds_id}"

        StandLogger.info(f"开始获取数据源信息: {ds_id}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api, headers=self.headers) as response:
                    if response.status == 404:
                        StandLogger.error(f"数据源不存在: {ds_id}")
                        raise Exception(f"数据源不存在: {ds_id}")

                    if response.status != 200:
                        error_str = await response.text()
                        error_msg = f"获取数据源信息失败, API: {api}, 状态码: {response.status}, 错误: {error_str}"
                        StandLogger.error(error_msg)
                        raise Exception(error_msg)

                    res = await response.json()
                    StandLogger.info(f"获取数据源信息: {ds_id} 结束")
                    return res

        except aiohttp.ClientError as e:
            error_msg = f"网络请求失败, API: {api}, 错误: {str(e)}"
            StandLogger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"获取数据源信息时发生异常, API: {api}, 错误: {str(e)}"
            StandLogger.error(error_msg)
            raise Exception(error_msg)

    async def decode_password(self, cipher_text: str) -> str:
        """
        RSA解密密码
        """
        try:
            # 读取私钥文件
            # import os
            # current_dir = os.path.dirname(os.path.abspath(__file__))
            # private_key_path = os.path.join(current_dir, 'private_key.txt')
            # with open(private_key_path, 'r') as f:
            #     private_key_pem = f.read()

            # # 清理私钥格式
            # clean_private_key = private_key_pem.replace("-----BEGIN PRIVATE KEY-----", "") \
            #     .replace("-----END PRIVATE KEY-----", "") \
            #     .replace("\\n", "").replace("\\r", "").replace(" ", "")

            clean_private_key = """MIIEwAIBADANBgkqhkiG9w0BAQEFAASCBKowggSmAgEAAoIBAQDbYY5JDWN4OGl3
PGEl11J/5TXQXgi+63uCJiFyEUAgmBGicxqYNPzoxKpBRzwN1MV08YubszcZQpyw
bWpsLdKqThcn02OZBduzsgxbJYRZCs3si/tLZCMNgkj6mm8g3TcjQqbdYqyaeuV7
ZsvNP9Ubx7vZhfr119cB6Jfq4OGG3W9r8nFlUUwhXekdroBBD2CflIBRNfZqQSFF
97Vs8mN9XKgz51822+B19qtqpXWs6FUMSp3Q2U5a3ZEfARNDBTyAgmJvZtqPYy3I
gBj59DAqUpbFSzUZwVsQKeFU+JU3oESFcPs6FG31AT9y5iXm/hrrKm6AZowErpUo
6oUcO9+bAgMBAAECggEBAMXsiwlfeemBw60enWsdi8H1koqN/Af7vi9apXwbEicV
63sLq+e8jpyWqiBA226DEy6BqfnsQ36XuXP3EzfMU67wyzVUIxxwy5mgvkMRYwlO
lSCf3jVTf8h1TdBCupYE3vUB8jf0CVNKI3Yk9SQVPfhVSCZlGVjpxYJkTYNMJkyc
GMYAdZFCEV43mIm+ev4GaepR+d/syeXL/SZfFa0uEy8SFChrehRDhdVVkn+dRzeg
O6tbDkTFYtOpi+UI5obcGsVXEN3ZAZzaOKrB2TPwU1Ei5sIcWZhvKEfJkpiKIdpe
eLztYSaRB6gjCqhYQ3wzaJQCnoNVz+XqVaRTcPdZfBECgYEA+34Xo43WjhSdWR/P
laqleXfcwCmsF4Za+2qZjXLW//D2SXQylRv6hMAcVg7qCJM5a95X5VTr5H7pQNHN
ungE5Oi9lvYlZYb+pmG2wRn+/ufBs6OjwR6aDw/bsqeDHVjPeFIrxFPeXNllEHe1
xtZuhXvxFjDXqIwzQa2WijT8hjMCgYEA31Ag3lj9bAF7dBTJn8yRPhZX4v3I5N3x
H7G5XVj75cwMk4RB1s4WN/uLsuVDzXmG7NXjZ2c6kMYk658TTPKznQwhDx3Jq7Mh
HSJklWDtcPOioFZzFkikfqHseAWGf9s/HxBgieLa3IuGR9hEJ4EjDHa43UDXGQD2
90QGX7qlSPkCgYEAh9FL8N8LzQVjCJu+XqSe4t+RjxGyR64eeoLSVGp9pBE84ORo
4NAQVhrt8qfxShpAO3oDW+2ly2uiiogDo71nXzw2D031WkQySCajLNveM0lz+ZDZ
QdVF+/ZjfrMqgvHQcblmu4tTni8lfmQ3/h8V5u7Nf193SCYXFFQr5Y3CBrMCgYEA
wBgWXg3g2WKhBqbHFd4L5oOj0FAM2ssMGv5vfJwJ+4++FbtEQ3n95ORONHJBE+SB
KwOGXTGQUG8R3Vl2ac+wr9x6J52xGDC7wGsQaOr69RmvAAu9biLI1WGGn2vpWdyI
fLlCwfnR2LtwpCal4fGU66jItxKKtSh+SQ9MCFbuzUkCgYEAvUZaQDKmjdSbtR7J
yRXWfXPf0DpUqYKDzP40VoPcoQVGBmZAmq92yl1DMqFBfYCueCv1aA7Ozt+RFgyV
bMdUcJ0qzhKdCnEaonlpJPlnZkfATj5vOLs+nwfsmyO0iwcjA2zjJHmBZM+Xg+tl
enZgox36xuiZZrGQd0jXRt134QM="""
            # 解码base64私钥
            key_bytes = b64decode(clean_private_key)

            # 创建RSA私钥对象
            private_key = RSA.import_key(key_bytes)

            # 创建RSA解密器
            cipher = PKCS1_v1_5.new(private_key)

            # 解码base64加密数据
            encrypted_data = b64decode(cipher_text)

            # RSA解密
            decrypted_data = cipher.decrypt(encrypted_data, None)

            if decrypted_data is None:
                raise Exception("RSA解密失败")

            return decrypted_data.decode("utf-8")

        except Exception as e:
            StandLogger.error(f"RSA解密失败: {str(e)}")
            raise Exception(f"RSA解密失败: {str(e)}")
