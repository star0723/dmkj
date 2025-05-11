import hashlib
import time
import json
from collections import OrderedDict
from datetime import datetime

def MainJson(orgin_json):
    """主函数：生成包含签名的JSON数据
    参数: 无
    返回值: 无（直接输出结果）
    """
    timestamp = str(int(time.time() * 1000))

    # 解析JSON并添加时间戳
    jsons=json.loads(orgin_json)
    jsons['timestamp']=timestamp

    # 排序并处理空值（确保键有序且空值用空字符串代替）
    sorted_jsons = OrderedDict((k, v if v is not None else "")for k,v in sorted(jsons.items()))

    # 生成JSON字符串并计算签名（包含时间戳的有序JSON生成签名）
    jsonToken = json.dumps(sorted_jsons, separators=(',', ':'), ensure_ascii=False)
    signToken=hashjson(jsonToken)
    sorted_jsons['signToken']=signToken

    # 最终排序和输出（再次排序所有键并生成最终JSON）
    sorted_jsons={key: value if value is not None else "" for key, value in sorted(sorted_jsons.items())}
    jsons=json.dumps(sorted_jsons, separators=(',', ':'), ensure_ascii=False)
    return jsons

def to_hex(byte_array):
    """将字节数组转换为十六进制字符串
    参数:
        byte_array (bytes): 需要转换的字节数组
    返回值:
        str: 十六进制字符串表示
    """
    return ''.join([f'{byte:02x}' for byte in byte_array])

def odd_string(string_hex):
    """提取十六进制字符串的奇数位字符（保留第2、4、6...位）
    参数:
        string_hex (str): 需要处理的十六进制字符串
    返回值:
        str: 提取后的奇数位字符串
    """
    return ''.join([string_hex[i] for i in range(len(string_hex)) if i % 2 != 0])

def even_string(string_hex):
    """提取十六进制字符串的偶数位字符（保留第1、3、5...位）
    参数:
        string_hex (str): 需要处理的十六进制字符串
    返回值:
        str: 提取后的偶数位字符串
    """
    return ''.join([string_hex[i] for i in range(len(string_hex)) if i % 2 == 0])

def hashjson(json):
    """生成JSON数据的签名（通过SHA-512 -> 奇偶位处理 -> MD5的加密流程）
    参数:
        json (str): 需要签名的JSON字符串
    返回值:
        str: MD5签名（大写格式）
    """
    key=even_string(odd_string(to_hex(sha512(json))))
    return hashlib.md5(key.encode('utf-8')).hexdigest().upper()

def sha512(json):
    """计算JSON数据的SHA-512哈希值（用于签名生成的中间步骤）
    参数:
        json (str): 需要计算的JSON字符串
    返回值:
        bytes: SHA-512哈希值的字节形式
    """
    return  hashlib.sha512(json.encode('utf-8')).digest()

