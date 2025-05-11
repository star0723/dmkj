import base64
import functools
import json
import random
from Crypto.Cipher import DES
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from Crypto.Util.Padding import pad as symmetric_pad
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
import os
from SignToken import MainJson

base64_characters ="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
aes_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
rsa_key = base64.b64decode("MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCe7YEyWa0T+WMXa8q1PQSo2N156Fz6c1iN0WLMm5dH1KBdGo/RHOfLOBhnKb/dgvayQUHfKzsCHw0Pm8pNESDhFVTl/Xndg3O4Al+L8XoD5GPeqHa8SGLorRnLOPhk6nTkqlPvFXNYAdyPzT6Y5171Ez1Q2FFcW4jUDTo5sFX2qwIDAQAB")#base64编码的RSA公钥
aes_iv  = base64.b64decode("MTYyODA5MjEyMTMxMjIxMw==")
des_key = b"51434574"
CREDENTIALS_PATH = "credentials.json"
JPUSH_ID = "465779ab14c3e283530"
VERSION = "4.7.3"

def randomKey():
    random_Key=[]
    for key in range(16):
        random_Key.append(random.choice(aes_characters))
    return ''.join(random_Key)
aes_key = randomKey().encode("utf-8")

def pad(data: bytes) -> bytes:
    """
    使用 PKCS#5 填充标准对字节数据进行填充。
    """
    block_size = 16
    padding_length = block_size - (len(data) % block_size)
    padding = bytes([padding_length] * padding_length)
    return data + padding

def aes_encrypt(key: bytes, iv: bytes, plaintext: str) -> bytes:
    plaintext_bytes = plaintext.encode('utf-8')
    padded_data = pad(plaintext_bytes)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(ciphertext)


# DES 加密函数
def des_encrypt(plain_text: str) -> str:
    cipher = DES.new(des_key, DES.MODE_ECB)
    padded_data = symmetric_pad(plain_text.encode("utf-8"), DES.block_size)
    encrypted_bytes = cipher.encrypt(padded_data)
    return encrypted_bytes.hex().upper()

def rsa_encrypt(public_key_der: bytes, plaintext: bytes, chunk_size: int = 117) -> bytes:
    public_key = serialization.load_der_public_key(
        public_key_der,
        backend=default_backend()
    )
    ciphertext = b''
    for i in range(0, len(plaintext), chunk_size):
        chunk = plaintext[i:i + chunk_size]
        ciphertext += public_key.encrypt(chunk, asymmetric_padding.PKCS1v15())
    return base64.b64encode(ciphertext)


def custom_base64_d(b_arr: bytes) -> str:
    # 自定义 Base64 字符表
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

    length = len(b_arr)
    sb = []
    full_group_end = length - (length % 3)
    group_counter = 0

    # 处理完整的 3 字节块
    for i in range(0, full_group_end, 3):
        combined = ((b_arr[i] & 0xFF) << 16) | ((b_arr[i + 1] & 0xFF) << 8) | (b_arr[i + 2] & 0xFF)
        sb.append(base64_chars[(combined >> 18) & 0x3F])
        sb.append(base64_chars[(combined >> 12) & 0x3F])
        sb.append(base64_chars[(combined >> 6) & 0x3F])
        sb.append(base64_chars[combined & 0x3F])

        group_counter += 1

        if group_counter == 14:
            sb.append(' ')
            group_counter = 0

    # 处理剩余字节
    remaining_bytes = length % 3
    if remaining_bytes == 1:
        combined = (b_arr[full_group_end] & 0xFF) << 16
        sb.append(base64_chars[(combined >> 18) & 0x3F])
        sb.append(base64_chars[(combined >> 12) & 0x3F])
        sb.append("==")
    elif remaining_bytes == 2:
        combined = ((b_arr[full_group_end] & 0xFF) << 16) | ((b_arr[full_group_end + 1] & 0xFF) << 8)
        sb.append(base64_chars[(combined >> 18) & 0x3F])
        sb.append(base64_chars[(combined >> 12) & 0x3F])
        sb.append(base64_chars[(combined >> 6) & 0x3F])
        sb.append("=")

    return ''.join(sb)
@functools.lru_cache(maxsize=1)
def load_credentials() -> tuple:
    """首次从磁盘读取 credentials.json，后续调用直接走缓存"""
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(f"{CREDENTIALS_PATH} not found")
    with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    uid = data.get("uid")
    token = data.get("token")
    if not uid or not token:
        raise ValueError("credentials.json missing 'uid' or 'token'")
    return uid, token


# 允许 main.py 在保存新凭证后更新缓存
def update_cached_credentials(uid: str, token: str):
    load_credentials.cache_clear()
    # 重新设置缓存结果
    load_credentials()
    # monkey-patch cached value
    load_credentials.cache_info()  # ensure cache exists
    load_credentials.__wrapped__ = lambda: (uid, token)  # override wrapped
    load_credentials.cache_clear()
    functools.lru_cache(maxsize=1)(load_credentials)


def get_cached_credentials() -> tuple:
    """获取当前内存缓存的 uid/token"""
    return load_credentials()

def PhoneLoginD():
    account = str(input("输入手机号"))
    pwd = str(input("输入密码"))
    login_data = {
        "jPushId": JPUSH_ID,
        "account": account,
        "pwd": des_encrypt(pwd),
        "version": "4.7.3"
    }
    loginJson = MainJson(json.dumps(login_data))
    Encryptaes=aes_encrypt(aes_key,  aes_iv, loginJson)
    Encryptras=rsa_encrypt(rsa_key, aes_key)
    Und = Encryptaes+Encryptras
    d="d="+custom_base64_d(Und)
    print(f'手机号登录{d}')
    return d
def TokenLoginD() -> str:
    """Token 登录，自动读取（缓存的）uid/token，返回 d=..."""
    uid, token = load_credentials()
    login_data = {
        "jPushId": JPUSH_ID,
        "token": token,
        "uid": uid,
        "version": "4.7.3",
    }
    loginJson = MainJson(json.dumps(login_data))
    Encryptaes=aes_encrypt(aes_key,  aes_iv, loginJson)
    Encryptras=rsa_encrypt(rsa_key, aes_key)
    Und = Encryptaes+Encryptras
    d="d="+custom_base64_d(Und)
    print(f'token登录{d}')
    return d
def ActivitiesD():
    uid, token= load_credentials()
    must_data={
        "catalogId":"",
        "catalogId2":"",
        "collegeFlag":"",
        "endTime":"",
        "jPushId":JPUSH_ID,
        "joinEndTime":"",
        "joinFlag":"1",
        "joinStartTime":"",
        "keyword":"",
        "level":"",
        "page":"1",
        "sort":"",
        "specialFlag":"",
        "startTime":"",
        "status":"",
        "token":token,
        "uid":uid,
        "version":"4.7.3"
    }
    Json = MainJson(json.dumps(must_data))
    Encryptaes=aes_encrypt(aes_key,  aes_iv, Json)
    Encryptras=rsa_encrypt(rsa_key, aes_key)
    Und = Encryptaes+Encryptras
    d="d="+custom_base64_d(Und)
    print(f'活动查询{d}')
    return d
def MainActivitiesD():
    activityID = input("请输入活动ID:")
    uid, token = load_credentials()
    must_data = {
        "activityId": activityID,
        "jPushId": JPUSH_ID,
        "token":token,
        "uid": uid,
        "version": "4.7.3"
    }
    Json = MainJson(json.dumps(must_data))
    Encryptaes=aes_encrypt(aes_key,  aes_iv, Json)
    Encryptras=rsa_encrypt(rsa_key, aes_key)
    Und = Encryptaes+Encryptras
    d="d="+custom_base64_d(Und)
    print(f'活动内容{d}')
    return d,activityID
def SubmitD(id):
    activityId = id
    uid, token = load_credentials()
    must_data = {
        "jPushId": JPUSH_ID,
        "uid": uid,
        "token": token,
        "data": "[]",
        "remark": "",
        "activityId": activityId,
        "version": "4.7.3"
    }
    Json = MainJson(json.dumps(must_data))
    Encryptaes=aes_encrypt(aes_key,  aes_iv, Json)
    Encryptras=rsa_encrypt(rsa_key, aes_key)
    Und = Encryptaes+Encryptras
    d="d="+custom_base64_d(Und)
    print(f'提交{d}')
    return d

def HomePageD():
    uid, token = load_credentials()
    must_data = {
        "jPushId": JPUSH_ID,
        "token": token,
        "uid": uid,
        "version": "4.7.3"
    }
    Json = MainJson(json.dumps(must_data),)
    Encryptaes=aes_encrypt(aes_key,  aes_iv, Json)
    Encryptras=rsa_encrypt(rsa_key, aes_key)
    Und = Encryptaes+Encryptras
    d="d="+custom_base64_d(Und)
    print(f'个人主页{d}')
    return d


















































''''\\\
\\.'''