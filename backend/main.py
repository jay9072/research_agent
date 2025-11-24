# backend/main.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
import os
from groq import Groq

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------
# 1) GitHub API 호출 (트렌드 필터 적용 버전)
# ---------------------------------------------------
def fetch_repos(query, days):
    # days = 180 / 365 / 1095
    date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    # 트렌드 필터 
    q = f"{query} stars:>10 forks:>2 created:>{date_from} in:name,description"

    params = {
        "q": q,
        "sort": "stars",
        "order": "desc",
        "per_page": 10,
    }

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    }

    url = "https://api.github.com/search/repositories"
    res = requests.get(url, params=params, headers=headers)
    res.raise_for_status()

    return res.json()["items"]


# ---------------------------------------------------
# 2) Groq 기반 기술 보고서 요약 생성
# ---------------------------------------------------
def summarize_repos_with_groq(repos, query):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # 레포를 텍스트로 변환
    repo_text = "\n".join(
        [f"- {r['full_name']}: {r['description']}" for r in repos]
    )

    # 전문 보고서 스타일 프롬프트
    prompt = f"""
당신은 산업 기술 분석 전문가이며, 전문적인 기술 보고서를 작성하는 역할입니다.

검색 주제: "{query}"

아래 GitHub 트렌드 레포들은 영어/일본어 등 여러 언어가 섞여있습니다.
이 설명들을 기반으로 **완전한 한국어 기술 분석 보고서**를 작성하세요.

반드시 지켜야 할 규칙:
- 결과물은 100% 자연스러운 한국어로만 작성
- 영어/일본어 등 외국어 문장은 모두 해석해서 한글로 변환
- 기술 용어(AI, ROS, Python 등)는 원문 유지
- 문체는 "기술 리포트" 문체 (격식 있고 논리적인 표현)
- 반드시 Markdown 구조 유지
- 전체 길이는 A4 1~1.5장 분량
- 레포 설명이 부족할 경우: "정보 부족"이라고 명시

보고서 형식 (반드시 이 틀을 따라 작성):

# 1. 서론
- 검색 주제의 산업적/기술적 배경 설명

# 2. 핵심 기술 트렌드 분석
- 현재 어떤 흐름이 나타나는지
- 트렌드별 의미

# 3. 주요 GitHub 레포 분석
각 레포마다 아래 형식으로 정리:
### ● {{repo 이름}}
- 주요 기능 요약
- 기술적 특징
- 산업 적용 가능성
- 의미 (왜 중요한가)

# 4. 기술 적용 분야 및 산업 전망
- 제조, 물류, 의료 등 기술 활용 가능성

# 5. 결론
- 종합 요약
- 향후 기술 발전 전망

아래는 분석해야 할 레포 목록입니다:

{repo_text}

위의 모든 조건을 충족하는 **전문 기술 분석 보고서**를 한국어로 작성하세요.
    """

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )

    return resp.choices[0].message.content


# ---------------------------------------------------
# 3) /summary (프론트 요청 처리)
# ---------------------------------------------------
@app.route("/summary", methods=["POST"])
def summary():
    data = request.get_json()
    query = data.get("query")
    days = int(data.get("days"))

    # 1) GitHub 트렌드 레포 가져오기
    repos = fetch_repos(query, days)

    # 2) Groq 기술 보고서 생성
    summary_text = summarize_repos_with_groq(repos, query)

    return jsonify({
        "repos": repos,
        "summary": summary_text
    })


# ---------------------------------------------------
# 서버 실행
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
