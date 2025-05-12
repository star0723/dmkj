import json
import requests
import gzip
import io
import time
import datetime
import Encode
from display import display_activities_pretty, display_activity_detail,countdown


# --- 配置项 ---
_, _, JPUSH_ID = Encode.get_cached_credentials()
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

def thanks():
    print("🙏 本程序由 KRIGERNM1G(star0723) 开源于 GitHub，纯公益项目，请勿倒卖 ❌")
    print("📣 感谢提供账号测试的同学，以及开源代码和思路支持的前辈！")


def main():
    print("📲 正在尝试登录…")

    if not token_login():
        while True:
            phone_login()
            # 读取 token 再验证
            try:
                d = Encode.TokenLoginD()
                uid, token, _= Encode.get_cached_credentials()
                resp = send_d_request(d, TOKEN_LOGIN, token)
                if resp.get("code") == "100":
                    print("✅ 手机号登录成功，进入主菜单！")
                    break
                else:
                    print(f"❌ 登录验证失败：{resp.get('msg') or '未知错误'}")
            except Exception as e:
                print(f"⚠️ 登录验证过程出错：{e}")
            print("🔁 请重新输入手机号进行登录...\n")
            time.sleep(1)  # 可选：避免刷屏

    # 登录成功后进入主菜单
    while True:
        print("\n====== 🛠 功能菜单 ======")
        print("1️⃣  查看活动列表")
        print("2️⃣  查看活动详情")
        print("3️⃣  执行抢报")
        print("4️⃣  退出程序")
        choice = input("👉 请输入选项编号：").strip()

        if choice == "1":
            activities()
        elif choice == "2":
            MainActivities()
        elif choice == "3":
            submit()
        elif choice == "4":
            print("👋 程序已退出，再见！")
            break
        else:
            print("❌ 无效选项，请输入 1~4 之间的数字")


def make_headers(token: str = None) -> dict:
    """🧾 构造请求头"""
    headers = {
        "Host": "appdmkj.5idream.net",
        "standardua": json.dumps(STANDARDUA),
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "okhttp/3.11.0"
    }
    return headers

def send_d_request(d_payload: str, url: str, token: str = None) -> dict:
    """📡 发送 d=… 请求，自动处理 gzip/异常"""
    try:
        resp = requests.post(
            url,
            headers=make_headers(token),
            data=d_payload.encode("utf-8"),
            timeout=10
        )
        resp.raise_for_status()
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
    except Exception as e:
        print(f"\n🚨 网络请求异常：{type(e).__name__} - {e}")
        print("⚠️ 请求失败，已跳过该操作，不会中断程序。")
        return {}

def save_credentials(account: str, uid: str, token: str):
    """💾 保存账号凭证"""
    with open(CRED_FILE, "w", encoding="utf-8") as f:
        json.dump({"account": account, "uid": uid, "token": token}, f, ensure_ascii=False, indent=2)
    Encode.update_cached_credentials(uid, token)

def token_login() -> bool:
    """🔑 使用 token 登录"""
    try:
        d = Encode.TokenLoginD()
        uid, token, _= Encode.get_cached_credentials()
    except Exception as e:
        print(f"⚠️ 无法读取本地凭证：{e}")
        return False

    print("🔐 使用 Token 登录中…")
    resp = send_d_request(d, TOKEN_LOGIN, token)
    if resp.get("code") == "100":
        print("✅ Token 登录成功！")
        return True
    else:
        print(f"❌ Token 登录失败：{resp.get('msg') or '未知错误'}")
        return False

def phone_login():
    """📞 使用手机号登录"""
    print("📞 正在尝试手机号登录…")
    d = Encode.PhoneLoginD()
    resp = send_d_request(d, LOGIN_URL)
    if resp.get("code") == "100":
        data = resp["data"]
        account = data.get("account") or input("📱 请输入手机号确认：")
        uid = str(data["uid"])
        token = data["token"]
        save_credentials(account, uid, token)
        print("✅ 手机号登录成功，凭证已保存！")
    else:
        print(f"❌ 手机号登录失败：{resp.get('msg') or '未知错误'}")

def activities():
    """📋 查看活动列表"""
    d = Encode.ActivitiesD()
    resp = send_d_request(d, ACTIVITIES_URL)
    print("📎 提示：因接口限制，部分活动可能无法完整显示，请使用手机链接获取 ID")
    if resp:
        display_activities_pretty(resp)

def MainActivities():
    """🔍 获取主活动 ID 和时间"""
    d, id = Encode.MainActivitiesD()
    resp = send_d_request(d, DETAIL_URL)
    if not resp:
        print("⚠️ 获取活动详情失败")
        return "", ""
    time_str = resp["data"].get('joindate')
    display_activity_detail(resp)
    return id, time_str

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
    deadline = time.time() + 30
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
        print("❌ 抢报超时，未在 30 秒内成功")


if __name__ == "__main__":
    thanks()
    main()
