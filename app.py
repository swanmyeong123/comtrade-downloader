import streamlit as st
import pandas as pd
import requests
import time
import datetime
from io import BytesIO

# --- 1. 국가 코드 정의 ---
# EU 27개국 리스트 (브렉시트 이후)
EU27_LIST = [
    "040", "056", "100", "191", "196", "203", "208", "233", "246", "251", 
    "276", "300", "348", "372", "380", "428", "440", "442", "470", "528", 
    "616", "620", "703", "705", "724", "752", "242"
]
EU27_STR = ",".join(EU27_LIST)

# CPTPP 등 기타 그룹
CPTPP_11_STR = "036,096,124,152,392,458,484,554,604,702,704" # 영국 미포함
UK_CODE = "826"

# [보고 국가(Reporter) 그룹]
REPORTER_GROUPS = {
    "직접 입력 (Custom)": "",

    "폴란드 (Poland)": "616",
    "독일 (Germany)": "276",
    "스페인 (Spain)": "724",
    "벨기에 (Belgium)": "056",
    "스웨덴 (Sweden)": "752",
    "한국 (Korea)": "410",
    "EU 27 전체 (All EU Members)": EU27_STR,
    "중국 (China)": "156",
    "미국 (USA)": "842",
}

# [상대국(Partner) 그룹]
PARTNER_GROUPS = {
    "직접 입력 (Custom)": "",
    "★ EU 27 역외 (Extra-EU) [World - EU27]": "EXTRA_EU_CALC", 
    "전 세계 합계 (World Total)": "0",
    "아프리카 (Africa)": "002",
    "아메리카 (Americas)": "019",
    "아시아 (Asia)": "142",
    "유럽 (Europe)": "150",
    "오세아니아 (Oceania)": "009",
    "EU 27 (역내 교역)": EU27_STR,
    "CPTPP (11개국 - 영국 미포함)": CPTPP_11_STR,
    "CPTPP (12개국 - 영국 포함)": CPTPP_11_STR + "," + UK_CODE,
    "미국 (USA)": "842",
    "중국 (China)": "156",
    "모든 개별 국가 (All Individual)": "all"
}

API_URL = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
current_year = datetime.datetime.now().year
YEAR_OPTIONS = [str(y) for y in range(current_year, 1999, -1)]

def get_comtrade_data(api_key, hs_code, single_year, reporter_code, partner_code, flow_code):
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    
    # EU 역외 계산 모드일 경우: World(0)와 EU27 국가들을 모두 요청
    if partner_code == "EXTRA_EU_CALC":
        actual_partner = "0," + EU27_STR
    else:
        actual_partner = partner_code

    clean_reporter = reporter_code.replace(" ", "")
    clean_partner = actual_partner.replace(" ", "")
    
    params = {
        "reporterCode": clean_reporter, 
        "partnerCode": clean_partner,
        "period": single_year,
        "cmdCode": str(hs_code).strip(),
        "flowCode": flow_code,
        "motCode": "0",
        "freqCode": "A",
        "format": "json"
    }

    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            df = pd.DataFrame(data['data'])
            
            # EU 역외 교역 계산 (World - EU_Sum)
            if partner_code == "EXTRA_EU_CALC":
                return calculate_extra_eu(df)
            else:
                return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error (HS:{hs_code}): {e}")
        return pd.DataFrame()

def calculate_extra_eu(df):
    """
    World 데이터에서 EU27 국가들의 데이터를 뺀 값을 계산하여 반환
    """
    try:
        df['primaryValue'] = pd.to_numeric(df['primaryValue'], errors='coerce').fillna(0)
        df['partnerCode'] = df['partnerCode'].astype(str)
        
        df_world = df[df['partnerCode'] == '0'].copy()
        df_eu = df[df['partnerCode'].isin(EU27_LIST)].copy()
        
        group_cols = ['reporterCode', 'reporterDesc', 'period', 'flowCode', 'flowDesc', 'cmdCode', 'cmdDesc']
        
        # EU 합계
        df_eu_sum = df_eu.groupby(group_cols)['primaryValue'].sum().reset_index()
        df_eu_sum = df_eu_sum.rename(columns={'primaryValue': 'euValue'})
        
        # 병합 및 차감
        merged = pd.merge(df_world, df_eu_sum, on=group_cols, how='left')
        merged['euValue'] = merged['euValue'].fillna(0)
        merged['extraEuValue'] = merged['primaryValue'] - merged['euValue']
        
        merged['primaryValue'] = merged['extraEuValue']
        merged['partnerCode'] = 'EXTRA_EU'
        merged['partnerDesc'] = 'EU27 Extra (Calculated)'
        
        return merged.drop(columns=['euValue', 'extraEuValue'])

    except Exception as e:
        print(f"Calculation Error: {e}")
        return pd.DataFrame()

def preprocess_dataframe(df, original_hs_codes):
    """
    다운로드용 데이터프레임 전처리:
    - 필요한 열만 선택 및 정리
    - 국가명 영문 열 추가 (reporterDesc, partnerDesc 활용)
    - cmdCode를 원본 형식 유지 (앞에 0 추가)
    - netWgt, primaryValue 열명에 단위 표시
    """
    if df.empty:
        return df
    
    result = df.copy()
    
    # cmdCode를 원본 HS 코드 형식으로 변환 (앞에 0 추가)
    hs_code_map = {code.lstrip('0'): code for code in original_hs_codes if code}
    hs_code_map.update({code: code for code in original_hs_codes if code})  # 원본도 매핑
    
    def format_cmdcode(code):
        code_str = str(code).strip()
        # 먼저 원본 매핑 확인
        if code_str in hs_code_map:
            return hs_code_map[code_str]
        # 숫자로 변환 후 매핑 확인
        code_stripped = code_str.lstrip('0')
        if code_stripped in hs_code_map:
            return hs_code_map[code_stripped]
        return code_str
    
    result['cmdCode'] = result['cmdCode'].apply(format_cmdcode)
    
    # 필요한 열 선택 및 순서 정렬
    columns_to_keep = [
        'period',
        'reporterCode', 'reporterDesc',
        'partnerCode', 'partnerDesc',
        'cmdCode',
        'netWgt', 'primaryValue'
    ]
    
    # 존재하는 열만 선택
    available_cols = [col for col in columns_to_keep if col in result.columns]
    result = result[available_cols]
    
    # 열 이름 변경: 국가명 열 및 단위 표시
    rename_map = {
        'reporterDesc': 'reporterName',
        'partnerDesc': 'partnerName',
        'netWgt': 'netWgt (kg)',
        'primaryValue': 'primaryValue (USD)'
    }
    result = result.rename(columns=rename_map)
    
    return result

# --- 웹페이지 UI ---
st.set_page_config(page_title="UN Comtrade 데이터 다운로더", layout="wide")

# [수정] 제목 및 작성자 표시
st.title("📦 UN Comtrade 데이터 다운로더")
st.markdown("""
    <div style='text-align: right; margin-top: -20px; color: #888888;'>
        작성자: Myeong suhwan
    </div>
    <hr>
    """, unsafe_allow_html=True)

st.markdown("보고 국가와 상대국을 직접 선택하거나, **EU 역외 교역**을 자동 계산할 수 있습니다.")

# 사이드바
with st.sidebar:
    st.header("🔑 API 설정")
    api_key = st.text_input("Subscription Key", type="password")
    
    st.write("---")
    st.subheader("⚙️ 교역 구분 (Flow)")
    flow_options = st.multiselect(
        "수집할 항목:",
        ["수입 (Import)", "수출 (Export)"],
        default=["수입 (Import)"]
    )
    
    flow_codes = []
    if "수입 (Import)" in flow_options: flow_codes.append("M")
    if "수출 (Export)" in flow_options: flow_codes.append("X")
    final_flow_code = ",".join(flow_codes)

# 메인 UI
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 보고 국가 (Reporter)")
    rep_choice = st.selectbox("보고 국가 선택:", list(REPORTER_GROUPS.keys()))
    
    if rep_choice == "직접 입력 (Custom)":
        reporter_code = st.text_input("보고국 코드 입력 (예: 251)", "251")
    else:
        reporter_code = REPORTER_GROUPS[rep_choice]
        st.info(f"Code: {reporter_code}")

with col2:
    st.subheader("2. 상대국 (Partner)")
    ptn_choice = st.selectbox("상대국 선택:", list(PARTNER_GROUPS.keys()))
    
    # 직접 입력 로직
    if ptn_choice == "직접 입력 (Custom)":
        partner_code_val = st.text_input("상대국 코드 입력 (예: 842 또는 842,156)", "0")
    else:
        partner_code_val = PARTNER_GROUPS[ptn_choice]
    
    if ptn_choice.startswith("★"):
        st.success("💡 [자동 계산] World - EU27 = EU 역외 실적 산출")
    elif ptn_choice != "직접 입력 (Custom)":
         display_code = (partner_code_val[:30] + '...') if len(partner_code_val) > 30 else partner_code_val
         st.caption(f"Code: {display_code}")

st.subheader("3. 연도 및 품목")
col3, col4 = st.columns([2, 1])
with col3:
    uploaded_file = st.file_uploader("HS 코드 파일 (CSV/TXT)", type=["csv", "txt"])
with col4:
    selected_years = st.multiselect("연도 선택:", YEAR_OPTIONS, default=["2023"])

if st.button("데이터 수집 시작", type="primary"):
    if not api_key or not uploaded_file or not reporter_code or not final_flow_code:
        st.warning("설정 정보를 모두 입력해주세요.")
    else:
        # 파일 읽기
        if uploaded_file.name.endswith('.csv'):
            df_input = pd.read_csv(uploaded_file, dtype=str)
            hs_codes = df_input.iloc[:, 0].dropna().tolist()
        else:
            stringio = uploaded_file.getvalue().decode("utf-8")
            hs_codes = [line.strip() for line in stringio.split('\n') if line.strip()]
        
        # 원본 HS 코드 형식 보존 (중복 제거 전)
        original_hs_codes = [c for c in hs_codes if c]
        hs_codes = list(set(original_hs_codes))
        target_years = sorted(selected_years, reverse=True)
        
        # 보고 국가 분할 (안전 요청)
        if "," in reporter_code:
            reporters_list = [r.strip() for r in reporter_code.split(',') if r.strip()]
        else:
            reporters_list = [reporter_code]

        total_tasks = len(hs_codes) * len(target_years) * len(reporters_list)
        st.write(f"📊 총 작업: {total_tasks}회 요청 예정")
        
        all_data = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        current_task = 0
        
        for code in hs_codes:
            for year in target_years:
                for rep in reporters_list:
                    current_task += 1
                    
                    status_text.text(f"Processing... HS:{code} | Year:{year} | Rep:{rep}")
                    
                    df_result = get_comtrade_data(api_key, code, year, rep, partner_code_val, final_flow_code)
                    
                    if not df_result.empty:
                        all_data.append(df_result)
                    
                    progress_bar.progress(current_task / total_tasks)
                    
                    time.sleep(1.2)
        
        status_text.text("✅ 완료!")
        
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            
            # 데이터 전처리 (열 정리)
            final_df = preprocess_dataframe(final_df, original_hs_codes)
            
            st.success(f"수집 성공! 총 {len(final_df)} 건.")
            
            # 미리보기
            st.dataframe(final_df.head())
            
            # 다운로드
            safe_ptn = "Custom" if ptn_choice == "직접 입력 (Custom)" else ptn_choice.split("(")[0].strip()
            csv = final_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 결과 다운로드 (CSV)",
                data=csv,
                file_name=f"TradeData_{safe_ptn}_{target_years[0]}.csv",
                mime="text/csv",
            )
        else:
            st.warning("데이터가 없습니다.")
