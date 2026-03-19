# Comtrade Downloader

UN Comtrade API 기반 국제무역 데이터 수집 및 시각화 도구.

## 기능

- Reporter(보고국) / Partner(상대국) 국가 선택 (개별 또는 그룹)
- HS 코드 선택 — 파일 업로드(CSV/TXT) 또는 콤보박스 직접 선택 (2/4/6자리)
- 연도 다중 선택
- 수입/수출 구분
- 결과 CSV/TSV 다운로드
- Alluvial Diagram (Reporter → HS Code → Partner 흐름 시각화)

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run comtradedownloader.py
```

## API 키

[UN Comtrade API](https://comtradeapi.un.org) 에서 Subscription Key를 발급받아 앱 사이드바에 입력합니다.
