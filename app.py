import streamlit as st
import pandas as pd
import requests
import time
import datetime
from io import BytesIO

# --- 1. 국가 코드 정의 --- #
# EU 27개국 리스트 (브렉시트 이후)
EU27_LIST = [
    "040", "056", "100", "191", "196", "203", "208", "233", "246", "251", "276", "300", "348", "372", "380", "428", "440", "442", "470", "528", "616", "620", "703", "705", "724", "752", "242"
]
EU27_STR = ",".join(EU27_LIST)

# CPTPP 등 기타 그룹
CPTPP_11_STR = "036,096,124,152,392,458,484,554,604,702,704" # 영국 미포함
UK_CODE = "826"

# UN M49 국가 코드 → 영문 국가명 매핑
COUNTRY_NAMES = {
    # World / Regions
    "0": "World",
    "002": "Africa",
    "009": "Oceania",
    "019": "Americas",
    "142": "Asia",
    "150": "Europe",

    # EU 27 Countries
    "040": "Austria",
    "056": "Belgium",
    "100": "Bulgaria",
    "191": "Croatia",
    "196": "Cyprus",
    "203": "Czechia",
    "208": "Denmark",
    "233": "Estonia",
    "246": "Finland",
    "251": "France",
    "242": "Fiji", # Note: This might be an error in EU27_LIST, as Fiji is not in EU
    "276": "Germany",
    "300": "Greece",
    "348": "Hungary",
    "372": "Ireland",
    "380": "Italy",
    "428": "Latvia",
    "440": "Lithuania",
    "442": "Luxembourg",
    "470": "Malta",
    "528": "Netherlands",
    "616": "Poland",
    "620": "Portugal",
    "703": "Slovakia",
    "705": "Slovenia",
    "724": "Spain",
    "752": "Sweden",

    # Other Major Countries
    "004": "Afghanistan", "008": "Albania", "012": "Algeria", "020": "Andorra", "024": "Angola",
    "028": "Antigua and Barbuda", "031": "Azerbaijan", "032": "Argentina", "036": "Australia",
    "044": "Bahamas", "048": "Bahrain", "050": "Bangladesh", "051": "Armenia", "052": "Barbados",
    "064": "Bhutan", "068": "Bolivia", "070": "Bosnia and Herzegovina", "072": "Botswana",
    "076": "Brazil", "084": "Belize", "090": "Solomon Islands", "096": "Brunei Darussalam",
    "104": "Myanmar", "108": "Burundi", "112": "Belarus", "116": "Cambodia", "120": "Cameroon",
    "124": "Canada", "132": "Cabo Verde", "140": "Central African Republic", "144": "Sri Lanka",
    "148": "Chad", "152": "Chile", "156": "China", "158": "Taiwan", "170": "Colombia",
    "174": "Comoros", "178": "Congo", "180": "DR Congo", "184": "Cook Islands", "188": "Costa Rica",
    "192": "Cuba", "204": "Benin", "212": "Dominica", "214": "Dominican Republic", "218": "Ecuador",
    "222": "El Salvador", "226": "Equatorial Guinea", "231": "Ethiopia", "232": "Eritrea",
    "234": "Faroe Islands", "238": "Falkland Islands", "242": "Fiji", "250": "France",
    "254": "French Guiana", "258": "French Polynesia", "262": "Djibouti", "266": "Gabon",
    "268": "Georgia", "270": "Gambia", "275": "Palestine", "288": "Ghana", "292": "Gibraltar",
    "296": "Kiribati", "304": "Greenland", "308": "Grenada", "312": "Guadeloupe", "316": "Guam",
    "320": "Guatemala", "324": "Guinea", "328": "Guyana", "332": "Haiti", "340": "Honduras",
    "344": "Hong Kong", "352": "Iceland", "356": "India", "360": "Indonesia", "364": "Iran",
    "368": "Iraq", "376": "Israel", "384": "Cote d'Ivoire", "388": "Jamaica", "392": "Japan",
    "398": "Kazakhstan", "400": "Jordan", "404": "Kenya", "408": "North Korea", "410": "South Korea",
    "414": "Kuwait", "417": "Kyrgyzstan", "418": "Laos", "422": "Lebanon", "426": "Lesotho",
    "430": "Liberia", "434": "Libya", "438": "Liechtenstein", "446": "Macao", "450": "Madagascar",
    "454": "Malawi", "458": "Malaysia", "462": "Maldives", "466": "Mali", "474": "Martinique",
    "478": "Mauritania", "480": "Mauritius", "484": "Mexico", "492": "Monaco", "496": "Mongolia",
    "498": "Moldova", "499": "Montenegro", "500": "Montserrat", "504": "Morocco", "508": "Mozambique",
    "512": "Oman", "516": "Namibia", "520": "Nauru", "524": "Nepal", "530": "Netherlands Antilles",
    "531": "Curacao", "533": "Aruba", "534": "Sint Maarten", "540": "New Caledonia",
    "548": "Vanuatu", "554": "New Zealand", "558": "Nicaragua", "562": "Niger", "566": "Nigeria",
    "570": "Niue", "574": "Norfolk Island", "578": "Norway", "580": "Northern Mariana Islands",
    "583": "Micronesia", "584": "Marshall Islands", "585": "Palau", "586": "Pakistan",
    "591": "Panama", "598": "Papua New Guinea", "600": "Paraguay", "604": "Peru", "608": "Philippines",
    "612": "Pitcairn", "630": "Puerto Rico", "634": "Qatar", "638": "Reunion", "642": "Romania",
    "643": "Russia", "646": "Rwanda", "654": "Saint Helena", "659": "Saint Kitts and Nevis",
    "660": "Anguilla", "662": "Saint Lucia", "666": "Saint Pierre and Miquelon",
    "670": "Saint Vincent and the Grenadines", "674": "San Marino", "678": "Sao Tome and Principe",
    "682": "Saudi Arabia", "686": "Senegal", "688": "Serbia", "690": "Seychelles", "694": "Sierra Leone",
    "702": "Singapore", "704": "Vietnam", "706": "Somalia", "710": "South Africa", "716": "Zimbabwe",
    "720": "Yemen", "728": "South Sudan", "729": "Sudan", "732": "Western Sahara", "740": "Suriname",
    "748": "Eswatini", "756": "Switzerland", "760": "Syria", "762": "Tajikistan", "764": "Thailand",
    "768": "Togo", "772": "Tokelau", "776": "Tonga", "780": "Trinidad and Tobago",
    "784": "United Arab Emirates", "788": "Tunisia", "792": "Turkey", "795": "Turkmenistan",
    "796": "Turks and Caicos Islands", "798": "Tuvalu", "800": "Uganda", "804": "Ukraine",
    "807": "North Macedonia", "818": "Egypt", "826": "United Kingdom", "831": "Guernsey",
    "832": "Jersey", "833": "Isle of Man", "834": "Tanzania", "840": "United States",
    "842": "United States", "850": "US Virgin Islands", "854": "Burkina Faso", "858": "Uruguay",
    "860": "Uzbekistan", "862": "Venezuela", "876": "Wallis and Futuna", "882": "Samoa",
    "887": "Yemen", "894": "Zambia",
    # Special codes
    "EXTRA_EU": "EU27 Extra (Calculated)",
    "all": "All Countries"
}

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
# 대륙별 국가 코드 (UN M49 기준)
CONTINENT_EUROPE = ["040","056","100","191","196","203","208","233","246","251","276","300","348","372","380","428","440","442","470","528","616","620","642","703","705","724","752","826","008","020","070","112","268","292","352","438","492","498","499","578","643","674","688","756","804","807"]
CONTINENT_AFRICA = ["012","024","072","108","120","132","140","148","174","178","180","204","226","231","232","262","266","270","288","324","384","404","426","430","450","454","466","478","480","504","508","516","562","566","646","686","690","694","706","710","716","728","729","732","748","768","788","800","834","854","894"]
CONTINENT_MIDDLE_EAST = ["048","364","368","376","400","414","422","512","634","682","760","784","887","275"]
CONTINENT_EAST_ASIA = ["156","392","410","158","344","446","408","496"]
CONTINENT_SOUTHEAST_ASIA = ["096","104","116","360","418","458","608","702","704","764"]
CONTINENT_NORTH_AMERICA = ["124","840","842"]
CONTINENT_CENTRAL_SOUTH_AMERICA = ["032","044","052","068","076","084","152","170","188","192","212","214","218","222","308","320","328","332","340","388","484","558","591","600","604","659","662","670","740","780","858","862"]
CONTINENT_OCEANIA = ["036","090","242","296","520","540","548","554","583","584","585","598","776","798","882"]

PARTNER_GROUPS = {
    "직접 입력 (Custom)": "",
    "--- 대륙별 선택 ---": "SEPARATOR",
    "🌍 유럽 (Europe)": ",".join(CONTINENT_EUROPE),
    "🌍 아프리카 (Africa)": ",".join(CONTINENT_AFRICA),
    "🌍 중동 (Middle East)": ",".join(CONTINENT_MIDDLE_EAST),
    "🌍 동아시아 (East Asia)": ",".join(CONTINENT_EAST_ASIA),
    "🌍 동남아시아 (Southeast Asia)": ",".join(CONTINENT_SOUTHEAST_ASIA),
    "🌍 북미 (North America)": ",".join(CONTINENT_NORTH_AMERICA),
    "🌍 중남미 (Central/South America)": ",".join(CONTINENT_CENTRAL_SOUTH_AMERICA),
    "🌍 오세아니아 (Oceania)": ",".join(CONTINENT_OCEANIA),
    "--- 기존 선택 ---": "SEPARATOR",
    "★ EU 27 역외 (Extra-EU) [World - EU27]": "EXTRA_EU_CALC",
    "전 세계 합계 (World Total)": "0",
    "EU 27 (역내 교역)": EU27_STR,
    "CPTPP (11개국 - 영국 미포함)": CPTPP_11_STR,
    "CPTPP (12개국 - 영국 포함)": CPTPP_11_STR + "," + UK_CODE,
    "미국 (USA)": "842",
    "중국 (China)": "156",
    "모든 개별 국가 (All Individual)": "all"
}

# 대륙 이름 매핑 (코드 → 대륙명)
def get_continent_name(country_code):
    """국가 코드로부터 대륙명 반환"""
    code = str(country_code).zfill(3)
    if code in CONTINENT_EUROPE: return "Europe"
    if code in CONTINENT_AFRICA: return "Africa"
    if code in CONTINENT_MIDDLE_EAST: return "Middle East"
    if code in CONTINENT_EAST_ASIA: return "East Asia"
    if code in CONTINENT_SOUTHEAST_ASIA: return "Southeast Asia"
    if code in CONTINENT_NORTH_AMERICA: return "North America"
    if code in CONTINENT_CENTRAL_SOUTH_AMERICA: return "Central/South America"
    if code in CONTINENT_OCEANIA: return "Oceania"
    return "Others"

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
    """ World 데이터에서 EU27 국가들의 데이터를 뺀 값을 계산하여 반환 """
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
    - 국가명 영문 열 추가 (COUNTRY_NAMES 딕셔너리 활용)
    - cmdCode를 원본 형식 유지 (앞에 0 추가)
    - netWgt, primaryValue 열명에 단위 표시
    """
    if df.empty:
        return df
        
    result = df.copy()
    
    # 국가 코드를 영문 국가명으로 변환하는 함수
    def get_country_name(code):
        code_str = str(code).strip()
        # 먼저 그대로 찾기
        if code_str in COUNTRY_NAMES:
            return COUNTRY_NAMES[code_str]
        # 앞에 0을 붙여서 찾기 (3자리로)
        padded_code = code_str.zfill(3)
        if padded_code in COUNTRY_NAMES:
            return COUNTRY_NAMES[padded_code]
        # 찾지 못하면 코드 그대로 반환
        return code_str

    # reporterCode와 partnerCode에서 영문 국가명 생성
    if 'reporterCode' in result.columns:
        result['reporterName'] = result['reporterCode'].apply(get_country_name)
    if 'partnerCode' in result.columns:
        result['partnerName'] = result['partnerCode'].apply(get_country_name)

    # cmdCode를 원본 HS 코드 형식으로 변환 (앞에 0 추가)
    hs_code_map = {code.lstrip('0'): code for code in original_hs_codes if code}
    hs_code_map.update({code: code for code in original_hs_codes if code}) # 원본도 매핑
    
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
        'reporterCode', 'reporterName',
        'partnerCode', 'partnerName',
        'flowCode',
        'cmdCode',
        'netWgt', 'primaryValue'
    ]
    # 존재하는 열만 선택
    available_cols = [col for col in columns_to_keep if col in result.columns]
    result = result[available_cols]

    # 열 이름 변경: 단위 표시
    rename_map = {
        'netWgt': 'netWgt (kg)',
        'primaryValue': 'primaryValue (USD)'
    }
    result = result.rename(columns=rename_map)
    
    return result

def create_alluvial_diagram(df):
    """ Plotly Sankey diagram 생성 Reporter → cmdCode → Partner (두께: netWgt) """
    import plotly.graph_objects as go
    
    if df.empty or 'netWgt (kg)' not in df.columns:
        return None
        
    # 결측치 제거 및 데이터 정리
    df_clean = df.copy()
    df_clean['netWgt (kg)'] = pd.to_numeric(df_clean['netWgt (kg)'], errors='coerce').fillna(0)
    df_clean = df_clean[df_clean['netWgt (kg)'] > 0]
    
    if df_clean.empty:
        return None
        
    # 노드 목록 생성
    reporters = df_clean['reporterName'].unique().tolist()
    cmdcodes = df_clean['cmdCode'].unique().tolist()
    partners = df_clean['partnerName'].unique().tolist()
    
    # cmdCode에 접두사 추가 (중복 방지)
    cmdcodes_prefixed = [f"HS-{c}" for c in cmdcodes]
    
    all_nodes = reporters + cmdcodes_prefixed + partners
    node_indices = {node: i for i, node in enumerate(all_nodes)}
    
    # 링크 1: Reporter → cmdCode
    link1 = df_clean.groupby(['reporterName', 'cmdCode'])['netWgt (kg)'].sum().reset_index()
    sources1 = [node_indices[r] for r in link1['reporterName']]
    targets1 = [node_indices[f"HS-{c}"] for c in link1['cmdCode']]
    values1 = link1['netWgt (kg)'].tolist()
    
    # 링크 2: cmdCode → Partner
    link2 = df_clean.groupby(['cmdCode', 'partnerName'])['netWgt (kg)'].sum().reset_index()
    sources2 = [node_indices[f"HS-{c}"] for c in link2['cmdCode']]
    targets2 = [node_indices[p] for p in link2['partnerName']]
    values2 = link2['netWgt (kg)'].tolist()
    
    # 모든 링크 결합
    sources = sources1 + sources2
    targets = targets1 + targets2
    values = values1 + values2
    
    # 노드 색상 설정
    node_colors = []
    for node in all_nodes:
        if node in reporters:
            node_colors.append('#2E86AB') # Reporter: 파란색
        elif node.startswith('HS-'):
            node_colors.append('#A23B72') # HS Code: 보라색
        else:
            node_colors.append('#F18F01') # Partner: 주황색
            
    # Sankey 다이어그램 생성
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color='rgba(100, 100, 100, 0.3)'
        )
    )])
    
    fig.update_layout(
        title_text="Alluvial Diagram: Reporter → HS Code → Partner (Weight: kg)",
        font_size=12,
        height=600
    )
    
    return fig

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
            
            # Alluvial Diagram 섹션
            st.write("---")
            st.subheader("📊 Alluvial Diagram (Reporter → HS Code → Partner)")
            st.caption("두께: 물량 (kg) 기준")
            
            try:
                fig = create_alluvial_diagram(final_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("다이어그램을 생성할 데이터가 충분하지 않습니다. (물량 데이터 필요)")
            except Exception as e:
                st.error(f"다이어그램 생성 오류: {e}")
        else:
            st.warning("데이터가 없습니다.")
