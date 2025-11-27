import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

# ==========================
# Slack Webhook URL (환경변수)
# ==========================
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# ==========================
# 키워드 파일 로드
# ==========================
def load_keywords():
    with open("keywords.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# ==========================
# PC / Mobile 검색 URL
# ==========================
def search_url(keyword, is_mobile=False):
    if is_mobile:
        return f"https://m.search.naver.com/search.naver?query={keyword}"
    return f"https://search.naver.com/search.naver?query={keyword}"

# ==========================
# 브랜드 검색 존재 여부 체크
# ==========================
def check_brand_search(keyword, is_mobile=False):
    url = search_url(keyword, is_mobile)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # 브랜드검색 블럭 탐지 (PC / MO 공통)
    brand_block = soup.find("div", class_="brand_block")

    if brand_block:
        return "☑️ 정상노출"
    else:
        return "❌ 미노출"

# ==========================
# Slack 메시지 전송
# ==========================
def send_slack_message(message: str):
    if not SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL is missing.")
        return

    payload = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

# ==========================
# 메인 실행 로직
# ==========================
def main():
    keywords = load_keywords()

    # 한국 시간 (KST)
    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.now(kst)
    now_str = now_kst.strftime("%Y-%m-%d %H:%M")

    # PC / Mobile 결과 생성
    pc_results = []
    mo_results = []

    for kw in keywords:
        pc_status = check_brand_search(kw, is_mobile=False)
        mo_status = check_brand_search(kw, is_mobile=True)

        pc_results.append(f"{kw} ({pc_status})")
        mo_results.append(f"{kw} ({mo_status})")

    # Slack 메시지 생성
    message = (
        f"📢 *BGROW - Naver Brand Search Monitoring*\n"
        f"⏱ {now_str} (KR Time)\n\n"
        f"*[PC]*\n" + "\n".join(pc_results) + "\n\n"
        f"*[MO]*\n" + "\n".join(mo_results)
    )

    # Slack 전송
    send_slack_message(message)

# ==========================
# Render Background Worker 실행
# ==========================
if __name__ == "__main__":
    main()
