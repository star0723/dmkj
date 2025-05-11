import datetime
import os
import json
import requests
import gzip
import io
import time
import datetime
import Encode
from display import display_activities_pretty, display_activity_detail,countdown

# --- 配置项 ---
JPUSH_ID = "465779ab14c3e283530"
STANDARDUA = {
    "channelName": "dmkj_Android",
    "countryCode": "CN",
    "createTime": 1733658187232,
    "device": "OnePlus HD1910",
    "hardware": "android_x86",
    "jPushId": JPUSH_ID,
    "modifyTime": 1733658187232,
    "operator": "中国移动",
    "screenResolution": "1080-1920",
    "startTime": 1733658388039,
    "sysVersion": "Android 25 7.1.2",
    "system": "android",
    "uuid": "689d891192d946d9baf7b74c47d42dcb",
    "version": "4.7.3"
}
CRED_FILE      = "credentials.json"
LOGIN_URL      = "https://appdmkj.5idream.net/v2/login/phone"
TOKEN_LOGIN    = "https://appdmkj.5idream.net/v2/login/loginByToken"
ACTIVITIES_URL = "https://appdmkj.5idream.net/v2/activity/activities"
DETAIL_URL     = "https://appdmkj.5idream.net/v2/activity/detail"
SUBMIT_URL     = "https://appdmkj.5idream.net/v2/signup/submit"
MINE_HOME      = "https://appdmkj.5idream.net/v3/user/mine_homepage"

def main():
    print("📲 正在尝试登录…")
    if not token_login():
        phone_login()
    while True:
        print("\n====== 🛠 功能菜单 ======")
        print("1. 查看活动列表")
        print("2. 查看活动详情")
        print("3. 执行抢报")
        print("4. 退出程序")
        choice = input("请输入选项编号：").strip()

        if choice == "1":
            activities()
        elif choice == "2":
            MainActivities()
        elif choice == "3":
            submit()
        elif choice == "4":
            print("👋 已退出程序")
            break
        else:
            print("❌ 无效选项，请输入 1~4 之间的数字")

def make_headers(token: str = None) -> dict:
    """构造请求头，支持带 token"""
    headers = {
        "Host": "appdmkj.5idream.net",
        "standardua": json.dumps(STANDARDUA),   # 默认 ensure_ascii=True，把中文转 \uXXXX
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "okhttp/3.11.0",
        # 不手动设置 Accept-Encoding，让 requests 自动处理 gzip/deflate
    }
    return headers

def send_d_request(
    d_payload: str,
    url: str,
    token: str = None
) -> dict:
    """发送 d=… 请求，优先用 requests 自动解压/解析 JSON"""
    resp = requests.post(
        url,
        headers=make_headers(token),
        data=d_payload.encode("utf-8")
    )
    resp.raise_for_status()

    # 1) 尝试 requests 自带的 JSON 解析（支持 gzip/deflate）
    try:
        return resp.json()
    except ValueError:
        content = resp.content
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(content)) as f:
                text = f.read().decode("utf-8")
        except (OSError, gzip.BadGzipFile):
            text = content.decode("utf-8", errors="ignore")
        return json.loads(text)

def save_credentials(account: str, uid: str, token: str):
    """存盘并更新内存缓存"""
    with open(CRED_FILE, "w", encoding="utf-8") as f:
        json.dump({"account": account, "uid": uid, "token": token},
                  f, ensure_ascii=False, indent=2)
    Encode.update_cached_credentials(uid, token)

def token_login() -> bool:
    """尝试用 token 登录"""
    try:
        d     = Encode.TokenLoginD()
        uid, token = Encode.get_cached_credentials()
    except Exception as e:
        print(f"错误信息: {e}")
        return False

    print("Token登录中")
    resp = send_d_request(d, TOKEN_LOGIN, token)  # ← 传入 token
    if resp.get("code") == "100":
        print("✅ Token登陆成功")
        return True
    else:
        print(f"⚠️ Token登陆失败: {resp.get('msg')}")
        return False

def phone_login():
    """手机号登录并保存凭证"""
    print("Performing phone login…")
    d    = Encode.PhoneLoginD()
    resp = send_d_request(d, LOGIN_URL)
    if resp.get("code") == "100":
        data    = resp["data"]
        account = data.get("account") or input("请输入手机号确认：")
        uid     = str(data["uid"])
        token   = data["token"]
        save_credentials(account, uid, token)
        print("✅ 登陆成功并保存相关数据")
        raise RuntimeError(f"手机号登陆失败: {resp}")


def activities():
    d = Encode.ActivitiesD()
    resp = send_d_request(d, ACTIVITIES_URL)
    print("由于BUG可参加活动显示不完全,可以根据手机分享链接进行ID获取")
    display_activities_pretty(resp)


def MainActivities():
    d,id= Encode.MainActivitiesD()
    resp = send_d_request(d, DETAIL_URL)
    time = resp["data"].get('joindate')
    display_activity_detail(resp)
    return id,time
def submit():
    id, time_str = MainActivities()
    futuretime = time_str.split("-")[0].strip()

    # 将活动开始时间转换为时间戳
    start_ts = datetime.datetime.strptime(futuretime, "%Y.%m.%d %H:%M").timestamp()

    # 运行倒计时（此处可为阻塞倒计时，主线程执行）
    countdown(start_ts)

    # 等待抢报窗口到达
    while True:
        diff = start_ts - time.time()
        if diff <= 0.05:
            break
        time.sleep(0.05)

    print("\n🚀 活动开始，进入抢报阶段（最多持续 45 秒，最多提交 4 次）")

    max_attempts = 4
    deadline = time.time() + 60
    attempt = 0

    while attempt < max_attempts and time.time() < deadline:
        try:
            d = Encode.SubmitD(id)
            resp = send_d_request(d, SUBMIT_URL)
            msg = resp.get("msg") or "无返回消息"
            print(f"[第{attempt+1}次提交] => {msg}")
            if "不能重复报名" in msg or resp.get("code") == "100":
                print("✅ 报名成功！")
                break
        except Exception as e:
            print(f"[错误] 第{attempt+1}次提交异常：{e}")
        attempt += 1

        if attempt < max_attempts:
            remaining_time = deadline - time.time()
            average_gap = remaining_time / (max_attempts - attempt)
            time.sleep(max(average_gap, 5))

    if attempt >= max_attempts:
        print("❌ 抢报失败，已达到最多尝试次数（4 次）")
    elif time.time() >= deadline:
        print("❌ 抢报超时，未在 45 秒内成功")


if __name__ == "__main__":
    main()
