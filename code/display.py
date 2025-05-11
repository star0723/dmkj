import sys
import time


def display_activities_pretty(resp):
    if resp.get("code") != "100":
        print("❌ 获取活动失败:", resp.get("msg"))
        return

    activities = resp["data"]["list"]
    print(f"\n📋 共 {len(activities)} 个活动（有更多：{resp['data']['haveMore']}）\n")
    for i, act in enumerate(activities, 1):
        print(f"{i:>2}. 【{act['name']}】")
        print(f"    📅 时间：{act['activitytime']}")
        print(f"    📌 状态：{act['statusText']}    分类：{act['catalog2name']}")
        print(f"    🆔 活动ID：{act['activityId']}")
        print()

def text_wrap(text: str, width=40):
    """将长段文字按指定宽度换行显示"""
    import textwrap
    return '\n'.join(textwrap.wrap(text, width=width))


def display_activity_detail(resp):
    if resp.get("code") != "100":
        print("❌ 获取详情失败:", resp.get("msg"))
        return

    data = resp["data"]
    print("\n🎉 活动详情")
    print("──────────────────────────────────────────")
    print(f"📌 活动名称   ：{data['activityName']}")
    print(f"🏫 举办学院   ：{data['collegename']}")
    print(f"🏷️ 活动标签   ：{data.get('labelname', '-')}")
    print(f"📅 活动时间   ：{data['startdate']}")
    print(f"🕐 报名时间   ：{data.get('joindate', '-')}")
    print(f"📍 活动地点   ：{data.get('address', '-')}")
    print(f"📖 活动分类   ：{data.get('catalog1name', '-')}/{data.get('catalog2name', '-')}")
    print(f"🔢 报名人数上限：{data.get('joinmaxnum', '不限')} 人")
    print(f"📝 报名方式   ：{data.get('joinWayDesc', '-').strip()}")
    print(f"🧠 参与限制   ：{data.get('joinrangeText', '-')}")
    print(f"🧮 学分奖励   ：{data['specialList'][0]['unitcount']} {data['specialList'][0]['accountTypeName']}" if data.get('specialList') else "🧮 学分奖励   ：无")
    print(f"🚫 报名状态   ：{data.get('unableJoinReason', '-') if data.get('ableJoinFlag') == 0 else '可以报名'}")
    print("──────────────────────────────────────────")
    print(f"📄 活动简介：\n{text_wrap(data.get('content', '无介绍'))}")
    print("──────────────────────────────────────────")
    if data.get("activityImgSet"):
        print(f"🖼️ 活动图片：{data['activityImgSet'][0]}")
    print()


def countdown(start_ts):
    """实时倒计时显示"""
    while True:
        now = time.time()
        diff = start_ts - now
        if diff <= 3:
            sys.stdout.write(f"\r\033[91m🔥 倒计时：{diff:.2f} 秒\033[0m")  # 红色
        if diff <= 0.1:
            print("\n🚀 时间到，开始抢报！")
            break
        sys.stdout.write(f"\r⏳ 倒计时：{diff:.2f} 秒")
        sys.stdout.flush()
        time.sleep(0.05 if diff < 10 else 1)
