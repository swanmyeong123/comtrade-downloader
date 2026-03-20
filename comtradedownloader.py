import streamlit as st
import pandas as pd
import requests
import time
import datetime
from io import BytesIO
from hs_code_data import HS2_CODES, HS4_CODES, HS6_CODES

# --- 1. 국가 코드 정의 ---
# EU 27개국 리스트 (브렉시트 이후)
EU27_LIST = [
    "040", "056", "100", "191", "196", "203", "208", "233", "246", "251", 
    "276", "300", "348", "372", "380", "428", "440", "442", "470", "528", 
    "616", "620", "703", "705", "724", "752", "642"
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
    "242": "Fiji",  # Note: This might be an error in EU27_LIST, as Fiji is not in EU
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
    "004": "Afghanistan",
    "008": "Albania",
    "012": "Algeria",
    "020": "Andorra",
    "024": "Angola",
    "028": "Antigua and Barbuda",
    "031": "Azerbaijan",
    "032": "Argentina",
    "036": "Australia",
    "044": "Bahamas",
    "048": "Bahrain",
    "050": "Bangladesh",
    "051": "Armenia",
    "052": "Barbados",
    "064": "Bhutan",
    "068": "Bolivia",
    "070": "Bosnia and Herzegovina",
    "072": "Botswana",
    "076": "Brazil",
    "084": "Belize",
    "090": "Solomon Islands",
    "096": "Brunei Darussalam",
    "104": "Myanmar",
    "108": "Burundi",
    "112": "Belarus",
    "116": "Cambodia",
    "120": "Cameroon",
    "124": "Canada",
    "132": "Cabo Verde",
    "140": "Central African Republic",
    "144": "Sri Lanka",
    "148": "Chad",
    "152": "Chile",
    "156": "China",
    "158": "Taiwan",
    "170": "Colombia",
    "174": "Comoros",
    "178": "Congo",
    "180": "DR Congo",
    "184": "Cook Islands",
    "188": "Costa Rica",
    "192": "Cuba",
    "204": "Benin",
    "212": "Dominica",
    "214": "Dominican Republic",
    "218": "Ecuador",
    "222": "El Salvador",
    "226": "Equatorial Guinea",
    "231": "Ethiopia",
    "232": "Eritrea",
    "234": "Faroe Islands",
    "238": "Falkland Islands",
    "242": "Fiji",
    "250": "France",
    "254": "French Guiana",
    "258": "French Polynesia",
    "262": "Djibouti",
    "266": "Gabon",
    "268": "Georgia",
    "270": "Gambia",
    "275": "Palestine",
    "288": "Ghana",
    "292": "Gibraltar",
    "296": "Kiribati",
    "304": "Greenland",
    "308": "Grenada",
    "312": "Guadeloupe",
    "316": "Guam",
    "320": "Guatemala",
    "324": "Guinea",
    "328": "Guyana",
    "332": "Haiti",
    "340": "Honduras",
    "344": "Hong Kong",
    "352": "Iceland",
    "356": "India",
    "360": "Indonesia",
    "364": "Iran",
    "368": "Iraq",
    "376": "Israel",
    "384": "Cote d'Ivoire",
    "388": "Jamaica",
    "392": "Japan",
    "398": "Kazakhstan",
    "400": "Jordan",
    "404": "Kenya",
    "408": "North Korea",
    "410": "South Korea",
    "414": "Kuwait",
    "417": "Kyrgyzstan",
    "418": "Laos",
    "422": "Lebanon",
    "426": "Lesotho",
    "430": "Liberia",
    "434": "Libya",
    "438": "Liechtenstein",
    "446": "Macao",
    "450": "Madagascar",
    "454": "Malawi",
    "458": "Malaysia",
    "462": "Maldives",
    "466": "Mali",
    "474": "Martinique",
    "478": "Mauritania",
    "480": "Mauritius",
    "484": "Mexico",
    "492": "Monaco",
    "496": "Mongolia",
    "498": "Moldova",
    "499": "Montenegro",
    "500": "Montserrat",
    "504": "Morocco",
    "508": "Mozambique",
    "512": "Oman",
    "516": "Namibia",
    "520": "Nauru",
    "524": "Nepal",
    "530": "Netherlands Antilles",
    "531": "Curacao",
    "533": "Aruba",
    "534": "Sint Maarten",
    "540": "New Caledonia",
    "548": "Vanuatu",
    "554": "New Zealand",
    "558": "Nicaragua",
    "562": "Niger",
    "566": "Nigeria",
    "570": "Niue",
    "574": "Norfolk Island",
    "578": "Norway",
    "580": "Northern Mariana Islands",
    "583": "Micronesia",
    "584": "Marshall Islands",
    "585": "Palau",
    "586": "Pakistan",
    "591": "Panama",
    "598": "Papua New Guinea",
    "600": "Paraguay",
    "604": "Peru",
    "608": "Philippines",
    "612": "Pitcairn",
    "630": "Puerto Rico",
    "634": "Qatar",
    "638": "Reunion",
    "642": "Romania",
    "643": "Russia",
    "646": "Rwanda",
    "654": "Saint Helena",
    "659": "Saint Kitts and Nevis",
    "660": "Anguilla",
    "662": "Saint Lucia",
    "666": "Saint Pierre and Miquelon",
    "670": "Saint Vincent and the Grenadines",
    "674": "San Marino",
    "678": "Sao Tome and Principe",
    "682": "Saudi Arabia",
    "686": "Senegal",
    "688": "Serbia",
    "690": "Seychelles",
    "694": "Sierra Leone",
    "702": "Singapore",
    "704": "Vietnam",
    "706": "Somalia",
    "710": "South Africa",
    "716": "Zimbabwe",
    "720": "Yemen",
    "728": "South Sudan",
    "729": "Sudan",
    "732": "Western Sahara",
    "740": "Suriname",
    "748": "Eswatini",
    "756": "Switzerland",
    "760": "Syria",
    "762": "Tajikistan",
    "764": "Thailand",
    "768": "Togo",
    "772": "Tokelau",
    "776": "Tonga",
    "780": "Trinidad and Tobago",
    "784": "United Arab Emirates",
    "788": "Tunisia",
    "792": "Turkey",
    "795": "Turkmenistan",
    "796": "Turks and Caicos Islands",
    "798": "Tuvalu",
    "800": "Uganda",
    "804": "Ukraine",
    "807": "North Macedonia",
    "818": "Egypt",
    "826": "United Kingdom",
    "831": "Guernsey",
    "832": "Jersey",
    "833": "Isle of Man",
    "834": "Tanzania",
    "840": "United States",
    "842": "United States",
    "850": "US Virgin Islands",
    "854": "Burkina Faso",
    "858": "Uruguay",
    "860": "Uzbekistan",
    "862": "Venezuela",
    "876": "Wallis and Futuna",
    "882": "Samoa",
    "887": "Yemen",
    "894": "Zambia",
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
CONTINENT_EUROPE = ["040","056","100","191","196","203","208","233","246","251","276","300","348","372","380","381","428","440","442","470","528","616","620","642","703","705","724","752","826","008","020","070","112","268","292","352","438","492","498","499","579","643","674","688","757","804","807"]
CONTINENT_AFRICA = ["012","024","072","108","120","132","140","148","174","178","180","204","226","231","232","262","266","270","288","324","384","404","426","430","450","454","466","478","480","504","508","516","562","566","646","686","690","694","706","710","716","728","729","732","748","768","788","800","834","854","894"]
CONTINENT_MIDDLE_EAST = ["048","364","368","376","400","414","422","512","634","682","760","784","887","275"]
CONTINENT_EAST_ASIA = ["156","392","410","158","344","446","408","496"]
CONTINENT_SOUTHEAST_ASIA = ["096","104","116","360","418","458","608","702","704","764"]
CONTINENT_NORTH_AMERICA = ["124","842"]
CONTINENT_CENTRAL_SOUTH_AMERICA = ["032","044","052","068","076","084","152","170","188","192","212","214","218","222","308","320","328","332","340","388","484","558","591","600","604","659","662","670","740","780","858","862"]
CONTINENT_OCEANIA = ["036","090","242","296","520","540","548","554","583","584","585","598","776","798","882"]

# 모든 대륙 국가를 합친 리스트 (대륙별 그룹화용)
ALL_CONTINENT_CODES = (CONTINENT_EUROPE + CONTINENT_AFRICA + CONTINENT_MIDDLE_EAST + 
                       CONTINENT_EAST_ASIA + CONTINENT_SOUTHEAST_ASIA + CONTINENT_NORTH_AMERICA + 
                       CONTINENT_CENTRAL_SOUTH_AMERICA + CONTINENT_OCEANIA)

PARTNER_GROUPS = {
    "직접 입력 (Custom)": "",
    "--- 대륙별 선택 ---": "SEPARATOR",
    "🌐 대륙별 통합 (All Continents)": "ALL_CONTINENTS",
    "🌍 유럽 (Europe)": ",".join(CONTINENT_EUROPE),
    "🌍 아프리카 (Africa)": ",".join(CONTINENT_AFRICA),
    "🌍 중동 (Middle East)": ",".join(CONTINENT_MIDDLE_EAST),
    "🌍 동아시아 (East Asia)": ",".join(CONTINENT_EAST_ASIA),
    "🌍 동남아시아 (Southeast Asia)": ",".join(CONTINENT_SOUTHEAST_ASIA),
    "🌍 북미 (North America)": ",".join(CONTINENT_NORTH_AMERICA),
    "🌍 중남미 (Central/South America)": ",".join(CONTINENT_CENTRAL_SOUTH_AMERICA),
    "🌍 오세아니아 (Oceania)": ",".join(CONTINENT_OCEANIA),
    "--- 기존 선택 ---": "SEPARATOR",
    "🔝 상위 N개국 + 기타 (Top N + Others)": "TOP5_AUTO",
    "전 세계 합계 (World Total)": "0",
    "EU 27 (역내 교역)": EU27_STR,
    "CPTPP (11개국 - 영국 미포함)": CPTPP_11_STR,
    "CPTPP (12개국 - 영국 포함)": CPTPP_11_STR + "," + UK_CODE,
    "미국 (USA)": "842",
    "중국 (China)": "156"
}


# 국가 코드 → 한글명 매핑
COUNTRY_NAMES = {
    # 동아시아
    "156": "중국", "344": "홍콩", "392": "일본", "408": "북한", "410": "한국", 
    "446": "마카오", "496": "몽골", "158": "대만",
    # 동남아시아
    "096": "브루나이", "104": "미얀마", "116": "캄보디아", "360": "인도네시아", 
    "418": "라오스", "458": "말레이시아", "608": "필리핀", "702": "싱가포르", 
    "764": "태국", "626": "동티모르", "704": "베트남",
    # 남아시아
    "004": "아프가니스탄", "050": "방글라데시", "064": "부탄", "356": "인도", 
    "462": "몰디브", "524": "네팔", "586": "파키스탄", "144": "스리랑카",
    # 중앙아시아
    "398": "카자흐스탄", "417": "키르기스스탄", "762": "타지키스탄", 
    "795": "투르크메니스탄", "860": "우즈베키스탄",
    # 서아시아 (중동)
    "051": "아르메니아", "031": "아제르바이잔", "048": "바레인", "196": "키프로스", 
    "268": "조지아", "368": "이라크", "376": "이스라엘", "400": "요르단", 
    "414": "쿠웨이트", "422": "레바논", "275": "팔레스타인", "512": "오만", 
    "634": "카타르", "682": "사우디아라비아", "760": "시리아", "792": "터키", 
    "784": "아랍에미리트", "887": "예멘",
    # 유럽 - 서유럽
    "040": "오스트리아", "056": "벨기에", "250": "프랑스", "251": "프랑스", "276": "독일", 
    "438": "리히텐슈타인", "442": "룩셈부르크", "492": "모나코", "528": "네덜란드", 
    "756": "스위스", "757": "스위스",
    # 유럽 - 북유럽
    "208": "덴마크", "233": "에스토니아", "246": "핀란드", "352": "아이슬란드", 
    "372": "아일랜드", "428": "라트비아", "440": "리투아니아", "578": "노르웨이", "579": "노르웨이", 
    "752": "스웨덴", "826": "영국",
    # 유럽 - 남유럽
    "008": "알바니아", "020": "안도라", "070": "보스니아헤르체고비나", "191": "크로아티아", 
    "292": "지브롤터", "300": "그리스", "336": "바티칸", "380": "이탈리아", "381": "이탈리아", 
    "470": "몰타", "499": "몬테네그로", "620": "포르투갈", "674": "산마리노", 
    "688": "세르비아", "705": "슬로베니아", "724": "스페인", "807": "북마케도니아",
    # 유럽 - 동유럽
    "112": "벨라루스", "100": "불가리아", "203": "체코", "348": "헝가리", 
    "616": "폴란드", "498": "몰도바", "642": "루마니아", "643": "러시아", 
    "703": "슬로바키아", "804": "우크라이나",
    # 북미
    "060": "버뮤다", "124": "캐나다", "304": "그린란드", "666": "생피에르미클롱", 
    "840": "미국", "842": "미국",
    # 중남미 - 중미
    "084": "벨리즈", "188": "코스타리카", "222": "엘살바도르", "320": "과테말라", 
    "340": "온두라스", "484": "멕시코", "558": "니카라과", "591": "파나마",
    # 중남미 - 카리브해
    "028": "앤티가바부다", "044": "바하마", "052": "바베이도스", "192": "쿠바", 
    "212": "도미니카", "214": "도미니카공화국", "308": "그레나다", "332": "아이티", 
    "388": "자메이카", "659": "세인트키츠네비스", "662": "세인트루시아", 
    "670": "세인트빈센트그레나딘", "780": "트리니다드토바고",
    # 중남미 - 남미
    "032": "아르헨티나", "068": "볼리비아", "076": "브라질", "152": "칠레", 
    "170": "콜롬비아", "218": "에콰도르", "328": "가이아나", "600": "파라과이", 
    "604": "페루", "740": "수리남", "858": "우루과이", "862": "베네수엘라",
    # 아프리카 - 북아프리카
    "012": "알제리", "818": "이집트", "434": "리비아", "504": "모로코", 
    "729": "수단", "788": "튀니지", "732": "서사하라",
    # 아프리카 - 동아프리카  
    "108": "부룬디", "086": "영국령인도양지역", "174": "코모로", "262": "지부티", 
    "232": "에리트레아", "231": "에티오피아", "404": "케냐", "480": "모리셔스", 
    "175": "마요트", "454": "말라위", "508": "모잠비크", "638": "레위니옹", 
    "646": "르완다", "690": "세이셸", "706": "소말리아", "728": "남수단", 
    "800": "우간다", "834": "탄자니아", "894": "잠비아", "716": "짐바브웨",
    # 아프리카 - 중앙아프리카
    "024": "앙골라", "120": "카메룬", "140": "중앙아프리카공화국", "148": "차드", 
    "178": "콩고", "180": "콩고민주공화국", "226": "적도기니", "266": "가봉", 
    "678": "상투메프린시페",
    # 아프리카 - 남아프리카
    "072": "보츠와나", "426": "레소토", "516": "나미비아", "710": "남아프리카공화국", 
    "748": "에스와티니",
    # 아프리카 - 서아프리카
    "204": "베냉", "132": "카보베르데", "270": "감비아", "288": "가나", 
    "324": "기니", "624": "기니비사우", "384": "코트디부아르", "430": "라이베리아", 
    "466": "말리", "478": "모리타니", "562": "니제르", "566": "나이지리아", 
    "654": "세인트헬레나", "686": "세네갈", "694": "시에라리온", "768": "토고", 
    "854": "부르키나파소",
    # 오세아니아
    "036": "호주", "162": "크리스마스섬", "166": "코코스제도", "554": "뉴질랜드", 
    "242": "피지", "540": "뉴칼레도니아", "598": "파푸아뉴기니", 
    "090": "솔로몬제도", "548": "바누아투"
}

# 국가 코드 → 영문명 매핑
COUNTRY_NAMES_ENG = {
    # 동아시아
    "156": "China", "344": "Hong Kong", "392": "Japan", "408": "North Korea", "410": "South Korea",
    "446": "Macao", "496": "Mongolia", "158": "Taiwan",
    # 동남아시아
    "096": "Brunei", "104": "Myanmar", "116": "Cambodia", "360": "Indonesia",
    "418": "Laos", "458": "Malaysia", "608": "Philippines", "702": "Singapore",
    "764": "Thailand", "626": "Timor-Leste", "704": "Vietnam",
    # 남아시아
    "004": "Afghanistan", "050": "Bangladesh", "064": "Bhutan", "356": "India",
    "462": "Maldives", "524": "Nepal", "586": "Pakistan", "144": "Sri Lanka",
    # 중앙아시아
    "398": "Kazakhstan", "417": "Kyrgyzstan", "762": "Tajikistan",
    "795": "Turkmenistan", "860": "Uzbekistan",
    # 서아시아 (중동)
    "051": "Armenia", "031": "Azerbaijan", "048": "Bahrain", "196": "Cyprus",
    "268": "Georgia", "368": "Iraq", "376": "Israel", "400": "Jordan",
    "414": "Kuwait", "422": "Lebanon", "275": "Palestine", "512": "Oman",
    "634": "Qatar", "682": "Saudi Arabia", "760": "Syria", "792": "Turkey",
    "784": "UAE", "887": "Yemen",
    # 유럽 - 서유럽
    "040": "Austria", "056": "Belgium", "250": "France", "251": "France", "276": "Germany",
    "438": "Liechtenstein", "442": "Luxembourg", "492": "Monaco", "528": "Netherlands",
    "756": "Switzerland", "757": "Switzerland",
    # 유럽 - 북유럽
    "208": "Denmark", "233": "Estonia", "246": "Finland", "352": "Iceland",
    "372": "Ireland", "428": "Latvia", "440": "Lithuania", "578": "Norway", "579": "Norway",
    "752": "Sweden", "826": "United Kingdom",
    # 유럽 - 남유럽
    "008": "Albania", "020": "Andorra", "070": "Bosnia Herzegovina", "191": "Croatia",
    "292": "Gibraltar", "300": "Greece", "336": "Vatican", "380": "Italy", "381": "Italy",
    "470": "Malta", "499": "Montenegro", "620": "Portugal", "674": "San Marino",
    "688": "Serbia", "705": "Slovenia", "724": "Spain", "807": "North Macedonia",
    # 유럽 - 동유럽
    "112": "Belarus", "100": "Bulgaria", "203": "Czechia", "348": "Hungary",
    "616": "Poland", "498": "Moldova", "642": "Romania", "643": "Russia",
    "703": "Slovakia", "804": "Ukraine",
    # 북미
    "060": "Bermuda", "124": "Canada", "304": "Greenland", "666": "St Pierre Miquelon",
    "840": "United States", "842": "United States",
    # 중남미 - 중미
    "084": "Belize", "188": "Costa Rica", "222": "El Salvador", "320": "Guatemala",
    "340": "Honduras", "484": "Mexico", "558": "Nicaragua", "591": "Panama",
    # 중남미 - 카리브해
    "028": "Antigua Barbuda", "044": "Bahamas", "052": "Barbados", "192": "Cuba",
    "212": "Dominica", "214": "Dominican Rep", "308": "Grenada", "332": "Haiti",
    "388": "Jamaica", "659": "St Kitts Nevis", "662": "St Lucia",
    "670": "St Vincent Grenadines", "780": "Trinidad Tobago",
    # 중남미 - 남미
    "032": "Argentina", "068": "Bolivia", "076": "Brazil", "152": "Chile",
    "170": "Colombia", "218": "Ecuador", "328": "Guyana", "600": "Paraguay",
    "604": "Peru", "740": "Suriname", "858": "Uruguay", "862": "Venezuela",
    # 아프리카 - 북아프리카
    "012": "Algeria", "818": "Egypt", "434": "Libya", "504": "Morocco",
    "729": "Sudan", "788": "Tunisia", "732": "Western Sahara",
    # 아프리카 - 동아프리카
    "108": "Burundi", "086": "British Indian Ocean", "174": "Comoros", "262": "Djibouti",
    "232": "Eritrea", "231": "Ethiopia", "404": "Kenya", "480": "Mauritius",
    "175": "Mayotte", "454": "Malawi", "508": "Mozambique", "638": "Reunion",
    "646": "Rwanda", "690": "Seychelles", "706": "Somalia", "728": "South Sudan",
    "800": "Uganda", "834": "Tanzania", "894": "Zambia", "716": "Zimbabwe",
    # 아프리카 - 중앙아프리카
    "024": "Angola", "120": "Cameroon", "140": "Central African Rep", "148": "Chad",
    "178": "Congo", "180": "DR Congo", "226": "Equatorial Guinea", "266": "Gabon",
    "678": "Sao Tome Principe",
    # 아프리카 - 남아프리카
    "072": "Botswana", "426": "Lesotho", "516": "Namibia", "710": "South Africa",
    "748": "Eswatini",
    # 아프리카 - 서아프리카
    "204": "Benin", "132": "Cabo Verde", "270": "Gambia", "288": "Ghana",
    "324": "Guinea", "624": "Guinea-Bissau", "384": "Cote d'Ivoire", "430": "Liberia",
    "466": "Mali", "478": "Mauritania", "562": "Niger", "566": "Nigeria",
    "654": "St Helena", "686": "Senegal", "694": "Sierra Leone", "768": "Togo",
    "854": "Burkina Faso",
    # 오세아니아
    "036": "Australia", "162": "Christmas Island", "166": "Cocos Islands", "554": "New Zealand",
    "242": "Fiji", "540": "New Caledonia", "598": "Papua New Guinea",
    "090": "Solomon Islands", "548": "Vanuatu"
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


# UN M49 기반 국가 목록 (지역별 그룹화)
COUNTRIES_BY_REGION = {
    "Africa": {
        "Northern Africa": ["012", "818", "434", "504", "729", "788", "732"],
        "Sub-Saharan Africa": {
            "Eastern Africa": ["108", "086", "174", "262", "232", "231", "404", "175", "454", "480", "508", "638", "646", "690", "706", "728", "800", "834", "716", "894"],
            "Middle Africa": ["024", "120", "140", "148", "266", "226", "178", "180", "678"],
            "Southern Africa": ["072", "748", "426", "516", "710"],
            "Western Africa": ["204", "132", "270", "288", "324", "624", "430", "466", "478", "562", "566", "654", "686", "694", "768", "854"]
        }
    },
    "Americas": {
        "Northern America": ["060", "124", "304", "666", "842"],  
        "Latin America and the Caribbean": {
            "Caribbean": ["660", "028", "533", "044", "052", "535", "136", "192", "531", "212", "214", "308", "312", "332", "388", "474", "500", "630", "652", "659", "662", "663", "670", "780", "796", "092", "850", "534"],
            "Central America": ["084", "188", "222", "320", "340", "484", "558", "591"],
            "South America": ["032", "068", "074", "076", "170", "218", "238", "254", "328", "600", "604", "239", "740", "858", "862"]
        }
    },
    "Asia": {
        "Central Asia": ["398", "417", "762", "795", "860"],
        "Eastern Asia": ["156", "344", "392", "408", "410", "446", "496", "158"],
        "Southern Asia": ["004", "050", "064", "356", "364", "462", "524", "586", "144"],
        "South-eastern Asia": ["096", "104", "116", "360", "418", "458", "608", "702", "764", "626", "704"],
        "Western Asia": ["051", "031", "048", "196", "268", "368", "376", "400", "414", "422", "275", "512", "634", "682", "760", "784", "792", "887"]
    },
    "Europe": {
        "Eastern Europe": ["112", "100", "203", "348", "616", "498", "642", "643", "703", "804", "807"],
        "Northern Europe": ["248", "208", "233", "234", "372", "352", "428", "440", "579", "744", "752", "826", "831", "832", "833"],
        "Southern Europe": ["008", "020", "070", "191", "292", "300", "336", "381", "470", "499", "620", "674", "688", "705", "724"],
        "Western Europe": ["040", "056", "251", "276", "438", "442", "492", "528", "757"]
    },
    "Oceania": {
        "Australia and New Zealand": ["036", "162", "166", "334", "554", "574"],
        "Melanesia": ["242", "540", "598", "090", "548"],
        "Micronesia": ["316", "296", "584", "583", "520", "580", "585"],
        "Polynesia": ["016", "184", "258", "570", "612", "772", "776", "798", "882", "876"]
    }
}


API_URL = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
current_year = datetime.datetime.now().year
YEAR_OPTIONS = [str(y) for y in range(current_year, 1999, -1)]

def get_comtrade_data(api_key, hs_code, single_year, reporter_code, partner_code, flow_code):
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    
    # 대륙별 통합 모드일 경우: 모든 대륙 국가 코드 전달
    if partner_code == "ALL_CONTINENTS":
        actual_partner = ",".join(ALL_CONTINENT_CODES)
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
            return pd.DataFrame(data['data'])
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error (HS:{hs_code}): {e}")
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
    def get_country_name_eng(code):
        code_str = str(code).strip()
        # partnerCode 0은 World로 표시
        if code_str == "0":
            return "World"
        # 먼저 그대로 찾기
        if code_str in COUNTRY_NAMES_ENG:
            return COUNTRY_NAMES_ENG[code_str]
        # 앞에 0을 붙여서 찾기 (3자리로)
        padded_code = code_str.zfill(3)
        if padded_code in COUNTRY_NAMES_ENG:
            return COUNTRY_NAMES_ENG[padded_code]
        # 찾지 못하면 빈 문자열 반환
        return ""
    
    # 국가 코드를 한글 국가명으로 변환하는 함수
    def get_country_name_kor(code):
        code_str = str(code).strip()
        # partnerCode 0은 World(전세계)로 표시
        if code_str == "0":
            return "World(전세계)"
        # 먼저 그대로 찾기
        if code_str in COUNTRY_NAMES:
            return COUNTRY_NAMES[code_str]
        # 앞에 0을 붙여서 찾기 (3자리로)
        padded_code = code_str.zfill(3)
        if padded_code in COUNTRY_NAMES:
            return COUNTRY_NAMES[padded_code]
        # 찾지 못하면 빈 문자열 반환
        return ""
    
    # 대륙명 영문 변환
    def get_continent_eng(code):
        code_str = str(code).zfill(3)
        return get_continent_name(code_str)
    
    # 대륙명 한글 변환
    def get_continent_kor(continent_eng):
        continent_map = {
            "Intra-EU27": "EU 역내",
            "Extra-EU27": "EU 역외",
            "Europe": "유럽",
            "Africa": "아프리카",
            "Middle East": "중동",
            "East Asia": "동아시아",
            "Southeast Asia": "동남아시아",
            "North America": "북미",
            "Central/South America": "중남미",
            "Oceania": "오세아니아",
            "Others": "기타"
        }
        return continent_map.get(continent_eng, "")
    
    # reporterCode에서 영문/한글/대륙명 생성
    if 'reporterCode' in result.columns:
        result['reporterName'] = result['reporterCode'].apply(get_country_name_eng)
        result['reporterNameKor'] = result['reporterCode'].apply(get_country_name_kor)
        result['reporterContinent'] = result['reporterCode'].apply(get_continent_eng)
        result['reporterContinentKor'] = result['reporterContinent'].apply(get_continent_kor)
    
    # partnerCode에서 영문/한글/대륙명 생성 (EU 역내/역외 구분)
    if 'partnerCode' in result.columns:
        result['partnerName'] = result['partnerCode'].apply(get_country_name_eng)
        result['partnerNameKor'] = result['partnerCode'].apply(get_country_name_kor)
        
        # Partner 대륙 구분 (EU 역내/역외 분리)
        def get_partner_continent_with_eu_split(code):
            code_str = str(code).zfill(3)
            if code_str in EU27_LIST:
                return "Intra-EU27"
            elif code_str in CONTINENT_EUROPE:
                return "Extra-EU27"
            else:
                return get_continent_name(code_str)
        
        result['partnerContinent'] = result['partnerCode'].apply(get_partner_continent_with_eu_split)
        result['partnerContinentKor'] = result['partnerContinent'].apply(get_continent_kor)
    
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
        'reporterCode', 'reporterName', 'reporterNameKor', 'reporterContinent', 'reporterContinentKor',
        'partnerCode', 'partnerName', 'partnerNameKor', 'partnerContinent', 'partnerContinentKor',
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

def remove_duplicates_with_report(df):
    """
    데이터프레임에서 완전히 중복된 행을 제거하고 중복 제거 리포트 생성
    
    완전히 동일한 행(모든 열의 값이 같은 경우)만 제거하며, 첫 번째 발견된 행을 유지합니다.
    
    Parameters:
    - df: 원본 데이터프레임
    
    Returns:
    - cleaned_df: 중복 제거된 데이터프레임
    - report: 중복 제거 리포트 딕셔너리
        - original_count: 원본 데이터 건수
        - cleaned_count: 중복 제거 후 데이터 건수
        - duplicates_removed: 제거된 중복 건수
        - reporter_duplicates: Reporter별 중복 제거 상세 정보
    """
    if df.empty:
        return df, {
            'original_count': 0,
            'cleaned_count': 0,
            'duplicates_removed': 0,
            'reporter_duplicates': {}
        }
    
    # 중복 제거 전 통계
    original_count = len(df)
    
    # Reporter별 중복 통계 (제거 전)
    # reporterCode 열이 없는 경우 처리
    if 'reporterCode' in df.columns:
        reporter_counts_before = df.groupby('reporterCode').size().to_dict()
    else:
        reporter_counts_before = {}
    
    # 완전히 중복된 행 제거 (모든 열이 동일한 경우, 첫 번째 행 유지)
    cleaned_df = df.drop_duplicates(keep='first')
    
    # 중복 제거 후 통계
    cleaned_count = len(cleaned_df)
    duplicates_removed = original_count - cleaned_count
    
    # Reporter별 중복 통계 (제거 후)
    if 'reporterCode' in cleaned_df.columns:
        reporter_counts_after = cleaned_df.groupby('reporterCode').size().to_dict()
    else:
        reporter_counts_after = {}
    
    # Reporter별 중복 제거 개수 계산
    reporter_duplicates = {}
    for reporter in reporter_counts_before:
        before = reporter_counts_before[reporter]
        after = reporter_counts_after.get(reporter, 0)
        removed = before - after
        if removed > 0:
            reporter_duplicates[reporter] = {
                'before': before,
                'after': after,
                'removed': removed
            }
    
    # 리포트 생성
    report = {
        'original_count': original_count,
        'cleaned_count': cleaned_count,
        'duplicates_removed': duplicates_removed,
        'reporter_duplicates': reporter_duplicates
    }
    
    return cleaned_df, report


def generate_trend_report(df):
    """
    조회된 무역 데이터를 바탕으로 동향 보고서 HTML 생성.
    - 총 교역 규모 (물량·금액)
    - 주요 상대국 TOP 5
    - 연도별 추이 (복수 연도)
    - 대륙별 현황
    """
    if df is None or df.empty:
        return None

    wgt_col = "netWgt (kg)"   if "netWgt (kg)"        in df.columns else None
    val_col = "primaryValue (USD)" if "primaryValue (USD)" in df.columns else None

    # ── 공통 수치 ──────────────────────────────────
    years       = sorted(df["period"].astype(str).unique()) if "period" in df.columns else []
    hs_codes    = sorted(df["cmdCode"].astype(str).unique()) if "cmdCode" in df.columns else []
    flow_labels = {"M": "수입", "X": "수출"}
    flows       = [flow_labels.get(str(f), str(f))
                   for f in df["flowCode"].unique()] if "flowCode" in df.columns else []

    reporter_col = "reporterNameKor" if "reporterNameKor" in df.columns else "reporterName"
    partner_col  = "partnerNameKor"  if "partnerNameKor"  in df.columns else "partnerName"
    cont_col     = "partnerContinentKor" if "partnerContinentKor" in df.columns else "partnerContinent"

    reporters = sorted(df[reporter_col].dropna().unique()) if reporter_col in df.columns else []

    total_wgt = df[wgt_col].sum() if wgt_col else None
    total_val = df[val_col].sum() if val_col else None

    # HS 코드 한글명 매핑
    hs_kor_map = {k: v.split("(")[0].strip() for k, v in {**HS2_CODES, **HS4_CODES, **HS6_CODES}.items()}

    # ── HTML 조각 생성 헬퍼 ────────────────────────
    def row(label, value, highlight=False):
        color = "#F28E2B" if highlight else "#1C2537"
        return (
            f"<div style='display:flex;justify-content:space-between;"
            f"padding:5px 0;border-bottom:1px solid #EEF1F5;'>"
            f"<span style='color:#5E6E82;font-size:13px;'>{label}</span>"
            f"<span style='color:{color};font-size:13px;font-weight:600;'>{value}</span></div>"
        )

    def section_title(title):
        return (
            f"<div style='margin:16px 0 8px;font-size:13px;font-weight:700;"
            f"color:#2E86AB;letter-spacing:0.3px;border-left:3px solid #2E86AB;"
            f"padding-left:8px;'>{title}</div>"
        )

    blocks = []

    # ── 1. 조회 개요 ───────────────────────────────
    year_str = f"{years[0]}" if len(years) == 1 else f"{years[0]} ~ {years[-1]} ({len(years)}개년)"
    hs_str   = ", ".join(hs_codes[:3]) + ("..." if len(hs_codes) > 3 else "")
    rep_str  = ", ".join(reporters[:3]) + ("..." if len(reporters) > 3 else "")
    flow_str = " · ".join(flows) if flows else "-"

    blocks.append(section_title("조회 개요"))
    blocks.append(row("기간",    year_str))
    blocks.append(row("보고국",  rep_str  or "-"))
    blocks.append(row("품목",    hs_str   or "-"))
    blocks.append(row("교역구분", flow_str))

    # ── 2. 총 교역 규모 ────────────────────────────
    blocks.append(section_title("총 교역 규모"))
    if total_wgt is not None:
        if total_wgt >= 1_000_000:
            wgt_disp = f"{total_wgt/1_000_000:,.1f} 천 톤"
        else:
            wgt_disp = f"{total_wgt/1_000:,.1f} 톤"
        blocks.append(row("총 물량", wgt_disp, highlight=True))
    if total_val is not None:
        if total_val >= 1_000_000:
            val_disp = f"USD {total_val/1_000_000:,.1f}백만"
        else:
            val_disp = f"USD {total_val/1_000:,.0f}천"
        blocks.append(row("총 금액", val_disp))

    # ── 3. 주요 상대국 TOP 5 ───────────────────────
    if wgt_col and partner_col in df.columns:
        partner_wgt = (
            df.groupby(partner_col, dropna=True)[wgt_col]
            .sum().sort_values(ascending=False)
        )
        partner_wgt = partner_wgt[partner_wgt.index.str.strip() != ""]
        top5 = partner_wgt.head(5)
        if not top5.empty and total_wgt and total_wgt > 0:
            blocks.append(section_title("주요 상대국 (물량 기준 TOP 5)"))
            for rank, (nation, wgt) in enumerate(top5.items(), 1):
                pct = wgt / total_wgt * 100
                if wgt >= 1_000_000:
                    wgt_d = f"{wgt/1_000_000:,.1f}천 톤"
                else:
                    wgt_d = f"{wgt/1_000:,.1f}톤"
                blocks.append(row(f"{rank}. {nation}", f"{wgt_d}  ({pct:.1f}%)"))

    # ── 4. 연도별 추이 (복수 연도) ─────────────────
    if wgt_col and len(years) > 1 and "period" in df.columns:
        yearly = (
            df.groupby(df["period"].astype(str))[wgt_col]
            .sum().sort_index()
        )
        blocks.append(section_title("연도별 물량 추이"))
        prev = None
        for yr, wgt in yearly.items():
            if wgt >= 1_000_000:
                wgt_d = f"{wgt/1_000_000:,.1f}천 톤"
            else:
                wgt_d = f"{wgt/1_000:,.1f}톤"
            if prev is not None and prev > 0:
                chg    = (wgt - prev) / prev * 100
                sign   = "+" if chg >= 0 else ""
                suffix = f"  ({sign}{chg:.1f}%)"
            else:
                suffix = ""
            blocks.append(row(str(yr), wgt_d + suffix))
            prev = wgt

    # ── 5. 대륙별 현황 ─────────────────────────────
    if wgt_col and cont_col in df.columns and total_wgt and total_wgt > 0:
        cont_wgt = (
            df.groupby(cont_col, dropna=True)[wgt_col]
            .sum().sort_values(ascending=False)
        )
        cont_wgt = cont_wgt[cont_wgt.index.str.strip() != ""]
        if not cont_wgt.empty:
            blocks.append(section_title("대륙별 현황 (물량 기준)"))
            for cont, wgt in cont_wgt.items():
                pct = wgt / total_wgt * 100
                if wgt >= 1_000_000:
                    wgt_d = f"{wgt/1_000_000:,.1f}천 톤"
                else:
                    wgt_d = f"{wgt/1_000:,.1f}톤"
                blocks.append(row(str(cont), f"{wgt_d}  ({pct:.1f}%)"))

    # ── 6. HS 코드별 현황 (복수 품목) ─────────────
    if wgt_col and len(hs_codes) > 1 and "cmdCode" in df.columns and total_wgt and total_wgt > 0:
        hs_wgt = (
            df.groupby("cmdCode", dropna=True)[wgt_col]
            .sum().sort_values(ascending=False)
        )
        blocks.append(section_title("품목별 현황 (물량 기준)"))
        for hs, wgt in hs_wgt.items():
            pct     = wgt / total_wgt * 100
            hs_name = hs_kor_map.get(str(hs).strip(), "")
            label   = f"{hs}  {hs_name}" if hs_name else str(hs)
            if wgt >= 1_000_000:
                wgt_d = f"{wgt/1_000_000:,.1f}천 톤"
            else:
                wgt_d = f"{wgt/1_000:,.1f}톤"
            blocks.append(row(label, f"{wgt_d}  ({pct:.1f}%)"))

    content = "\n".join(blocks)
    return (
        "<div style='background:#FFFFFF;border:1px solid #DCE3ED;border-radius:8px;"
        "padding:20px 24px;margin-top:8px;'>"
        + content +
        "</div>"
    )


def create_alluvial_diagram(df, font_size=20,
                            reporter_color='#2E86AB', 
                            hscode_color='#A23B72', partner_color='#F18F01',
                            reporter_font_color='#000000',
                            hscode_font_color='#000000',
                            partner_font_color='#000000',
                            link_opacity=0.3, diagram_height=600, 
                            node_thickness=20,
                            group_by_continent=False, 
                            custom_title="",
                            merge_eu27_reporter=False,
                            show_hscode_percentage=False,
                            show_partner_percentage=False,
                            top_n_partners=None,
                            partner_sort_order="descending",
                            node_order="Reporter-HS-Partner",
                            use_korean_labels=False):
    """
    Plotly Sankey diagram 생성
    Reporter → cmdCode → Partner (두께: netWgt)
    
    Parameters:
    - font_size: 폰트 크기 (기본값: 20)
    - reporter_color: Reporter 노드 색상
    - hscode_color: HS Code 노드 색상
    - partner_color: Partner 노드 색상
    - reporter_font_color: Reporter 폰트 색상
    - hscode_font_color: HS Code 폰트 색상
    - partner_font_color: Partner 폰트 색상
    - link_opacity: 링크 투명도 (0~1)
    - diagram_height: 다이어그램 높이 (px)
    - node_thickness: 노드 두께 (기본값: 20)
    - group_by_continent: True면 국가를 대륙별로 그룹화
    - custom_title: 제목 문자열 (빈 문자열이면 표시 안함)
    - merge_eu27_reporter: True면 EU27 국가 Reporter를 "EU27"로 통합
    - show_hscode_percentage: True면 HS Code에 비율 표시
    - show_partner_percentage: True면 Partner에 비율 표시
    - top_n_partners: 상위 N개국만 표시, 나머지는 "기타"로 그룹화 (None이면 전체 표시)
    - partner_sort_order: Partner 정렬 순서 ("ascending" 또는 "descending")
    - node_order: 노드 순서 ("Reporter-HS-Partner", "Reporter-Partner-HS", "HS-Reporter-Partner" 등)
    - use_korean_labels: True면 노드 레이블을 한글로 변환
    """
    import plotly.graph_objects as go
    
    # HS Code 한글 매핑 (hs_code_data 모듈 기반 동적 구성)
    HS_CODE_KOREAN = {}
    for _code, _desc in {**HS2_CODES, **HS4_CODES, **HS6_CODES}.items():
        HS_CODE_KOREAN[_code] = _desc.split("(")[0].strip()
    
    if df.empty or 'netWgt (kg)' not in df.columns:
        return None
    
    # 결측치 제거 및 데이터 정리
    df_clean = df.copy()
    df_clean['netWgt (kg)'] = pd.to_numeric(df_clean['netWgt (kg)'], errors='coerce').fillna(0)
    df_clean = df_clean[df_clean['netWgt (kg)'] > 0]
    
    if df_clean.empty:
        return None
    
    # EU27 Reporter 통합 (EU27 국가를 "EU27"로 표시)
    if merge_eu27_reporter and 'reporterCode' in df_clean.columns:
        # EU27 국가들의 reporterContinentKor를 "EU27"로 변경
        def get_reporter_continent_display(row):
            code = str(row['reporterCode']).zfill(3) if 'reporterCode' in row.index else None
            if code and code in EU27_LIST:
                return "EU27"
            # reporterContinentKor가 있으면 사용, 없으면 reporterName 사용
            if 'reporterContinentKor' in row.index:
                return row['reporterContinentKor']
            elif 'reporterName' in row.index:
                return row['reporterName']
            return str(code) if code else "Unknown"
        
        df_clean['reporterDisplay'] = df_clean.apply(get_reporter_continent_display, axis=1)
        
        # ✅ EU27로 통합된 reporter들의 데이터를 그룹화하여 합산
        # partnerCode를 유지하면서 partnerName도 함께 사용
        if 'partnerCode' in df_clean.columns and 'partnerName' in df_clean.columns:
            # partnerCode와 partnerName 모두 유지 (대륙별 그룹화를 위해)
            df_grouped = df_clean.groupby(['reporterDisplay', 'cmdCode', 'partnerCode', 'partnerName'])['netWgt (kg)'].sum().reset_index()
        elif 'partnerCode' in df_clean.columns:
            df_grouped = df_clean.groupby(['reporterDisplay', 'cmdCode', 'partnerCode'])['netWgt (kg)'].sum().reset_index()
        else:
            partner_col = 'partnerName'
            df_grouped = df_clean.groupby(['reporterDisplay', 'cmdCode', partner_col])['netWgt (kg)'].sum().reset_index()
        # reporterDisplay를 reporterName으로 사용
        df_grouped = df_grouped.rename(columns={'reporterDisplay': 'reporterName'})
        df_clean = df_grouped
    
    # 대륙별 그룹화 적용 (유럽을 Intra/Extra-EU27로 분리)
    if group_by_continent and 'partnerCode' in df_clean.columns:
        def get_continent_with_eu_split(code):
            """유럽을 Intra-EU27과 Extra-EU27로 분리"""
            code_str = str(code).zfill(3)
            if code_str in EU27_LIST:
                return "Intra-EU27"
            elif code_str in CONTINENT_EUROPE:
                return "Extra-EU27"
            # 기존 대륙 분류
            if code_str in CONTINENT_AFRICA: return "Africa"
            if code_str in CONTINENT_MIDDLE_EAST: return "Middle East"
            if code_str in CONTINENT_EAST_ASIA: return "East Asia"
            if code_str in CONTINENT_SOUTHEAST_ASIA: return "Southeast Asia"
            if code_str in CONTINENT_NORTH_AMERICA: return "North America"
            if code_str in CONTINENT_CENTRAL_SOUTH_AMERICA: return "Central/South America"
            if code_str in CONTINENT_OCEANIA: return "Oceania"
            return "Others"
        
        df_clean['partnerContinent'] = df_clean['partnerCode'].apply(get_continent_with_eu_split)
        # 대륙별로 물량 합산
        df_grouped = df_clean.groupby(['reporterName', 'cmdCode', 'partnerContinent'])['netWgt (kg)'].sum().reset_index()
        df_grouped = df_grouped.rename(columns={'partnerContinent': 'partnerName'})
        df_clean = df_grouped
    
    # 노드 목록 생성
    reporters = df_clean['reporterName'].unique().tolist()
    cmdcodes = df_clean['cmdCode'].unique().tolist()
    
    # TOP5 모드에서 World(전세계) 제외 - partnerCode "0" 또는 partnerName이 "World"인 경우
    # 하지만 개별 국가 데이터가 없으면 World를 유지 (백업)
    world_filtered = False  # World 필터링 여부 추적
    if top_n_partners is not None:
        # partnerCode가 있는 경우 코드로 필터링
        if 'partnerCode' in df_clean.columns:
            df_no_world = df_clean[df_clean['partnerCode'].astype(str) != '0'].copy()
        else:
            df_no_world = df_clean.copy()
        
        # partnerName으로 필터링 (World 제외)
        df_no_world = df_no_world[~df_no_world['partnerName'].str.contains('World', case=False, na=False)].copy()
        
        # 개별 국가 데이터가 있으면 사용, 없으면 World 유지
        if len(df_no_world) > 0:
            df_clean = df_no_world
            world_filtered = True
        # else: World 데이터 유지 (경고는 다이어그램 생성 후 표시)
    
    # Partner를 물량 기준 정렬 (ascending/descending)
    ascending_order = (partner_sort_order == "ascending")
    partner_volumes = df_clean.groupby('partnerName')['netWgt (kg)'].sum().sort_values(ascending=ascending_order)
    partners = partner_volumes.index.tolist()
    
    # 상위 N개국만 표시, 나머지는 "기타"로 그룹화
    if top_n_partners is not None and len(partners) > top_n_partners:
        top_partners = partners[:top_n_partners]
        other_partners = partners[top_n_partners:]
        
        # 데이터프레임에서 "기타" 그룹으로 변환
        df_clean = df_clean.copy()
        df_clean['partnerName'] = df_clean['partnerName'].apply(
            lambda x: x if x in top_partners else '기타'
        )
        # "기타"를 합산하여 재계산
        df_clean = df_clean.groupby(['reporterName', 'cmdCode', 'partnerName'])['netWgt (kg)'].sum().reset_index()
        
        # Partner 다시 정렬
        partner_volumes = df_clean.groupby('partnerName')['netWgt (kg)'].sum().sort_values(ascending=ascending_order)
        partners = partner_volumes.index.tolist()
    
    # 전체 물량 계산 (비율 계산용)
    total_volume = df_clean['netWgt (kg)'].sum()
    
    # HS Code별 물량 계산
    hscode_volumes = df_clean.groupby('cmdCode')['netWgt (kg)'].sum()
    
    # Reporter 한글 변환 (use_korean_labels=True 시)
    # EU27 통합된 경우 "EU27" 문자열을 직접 처리하고, 개별 국가는 매핑 사용
    if 'reporterCode' in df.columns and 'reporterName' in df.columns:
        # ✅ DataFrame 기반 안전한 매핑 생성 (zip 대신 사용)
        # reporterName과 reporterCode의 실제 대응 관계 유지
        reporter_name_to_code = (
            df[['reporterName', 'reporterCode']]
            .drop_duplicates()
            .set_index('reporterName')['reporterCode']
            .to_dict()
        )
    else:
        reporter_name_to_code = {}
    
    reporters_display = []
    for r in reporters:
        # ✅ EU27 특별 처리: merge_eu27_reporter가 True일 때 "EU27"로 통합됨
        if r == "EU27":
            # 한글/영문 모두 "EU27"로 표시
            reporters_display.append("EU27")
        elif use_korean_labels:
            # reporterName에서 코드를 찾고, 코드로 한글명 조회
            code = reporter_name_to_code.get(r, '')
            code_str = str(code).zfill(3) if code else ''
            korean_name = COUNTRY_NAMES.get(code_str, r)
            reporters_display.append(korean_name)
        else:
            reporters_display.append(r)
    
    # cmdCode에 접두사 추가 및 한글 변환 (비율 포함 여부에 따라)
    cmdcodes_prefixed = []
    for c in cmdcodes:
        if use_korean_labels:
            # HS Code 한글 변환
            korean_hs = HS_CODE_KOREAN.get(c, f"HS-{c}")
            if show_hscode_percentage and total_volume > 0:
                pct = (hscode_volumes.get(c, 0) / total_volume) * 100
                cmdcodes_prefixed.append(f"{korean_hs}\n({pct:.1f}%)")
            else:
                cmdcodes_prefixed.append(korean_hs)
        else:
            # 영문명 (기존)
            if show_hscode_percentage and total_volume > 0:
                pct = (hscode_volumes.get(c, 0) / total_volume) * 100
                cmdcodes_prefixed.append(f"HS-{c}\n({pct:.1f}%)")
            else:
                cmdcodes_prefixed.append(f"HS-{c}")
    
    # Partner 레이블 및 한글 변환 (비율 포함 여부에 따라)
    partners_labeled = []
    for p in partners:
        if use_korean_labels:
            # Partner 한글 변환 (대륙명 변환)
            korean_partner_map = {
                "Intra-EU27": "EU 역내",
                "Extra-EU27": "EU 역외",
                "Europe": "유럽",
                "Africa": "아프리카",
                "Middle East": "중동",
                "East Asia": "동아시아",
                "Southeast Asia": "동남아시아",
                "North America": "북미",
                "Central/South America": "중남미",
                "Oceania": "오세아니아",
                "Others": "기타"
            }
            korean_p = korean_partner_map.get(p, COUNTRY_NAMES.get(str(p), p))
            if show_partner_percentage and total_volume > 0:
                pct = (partner_volumes.get(p, 0) / total_volume) * 100
                partners_labeled.append(f"{korean_p}\n({pct:.1f}%)")
            else:
                partners_labeled.append(korean_p)
        else:
            # 영문명 (기존)
            if show_partner_percentage and total_volume > 0:
                pct = (partner_volumes.get(p, 0) / total_volume) * 100
                partners_labeled.append(f"{p}\n({pct:.1f}%)")
            else:
                partners_labeled.append(p)
    
    all_nodes = reporters_display + cmdcodes_prefixed + partners_labeled
    
    node_indices = {node: i for i, node in enumerate(all_nodes)}
    
    # 원본 cmdCode와 레이블 매핑
    cmdcode_to_label = {c: cmdcodes_prefixed[i] for i, c in enumerate(cmdcodes)}
    partner_to_label = {p: partners_labeled[i] for i, p in enumerate(partners)}
    
    # 링크 생성 (Reporter → HS Code → Partner)
    # Reporter-HS 링크
    link_rep_hs = df_clean.groupby(['reporterName', 'cmdCode'])['netWgt (kg)'].sum().reset_index()
    reporter_to_display = {r: reporters_display[i] for i, r in enumerate(reporters)}
    sources_rep_hs = [node_indices[reporter_to_display[r]] for r in link_rep_hs['reporterName']]
    targets_rep_hs = [node_indices[cmdcode_to_label[c]] for c in link_rep_hs['cmdCode']]
    values_rep_hs = link_rep_hs['netWgt (kg)'].tolist()
    
    # HS-Partner 링크
    link_hs_ptn = df_clean.groupby(['cmdCode', 'partnerName'])['netWgt (kg)'].sum().reset_index()
    sources_hs_ptn = [node_indices[cmdcode_to_label[c]] for c in link_hs_ptn['cmdCode']]
    targets_hs_ptn = [node_indices[partner_to_label[p]] for p in link_hs_ptn['partnerName']]
    values_hs_ptn = link_hs_ptn['netWgt (kg)'].tolist()
    
    # 최종 링크 결합
    sources = sources_rep_hs + sources_hs_ptn
    targets = targets_rep_hs + targets_hs_ptn
    values = values_rep_hs + values_hs_ptn
    
    # 대륙별 색상 매핑 (Intra/Extra-EU27 포함)
    continent_colors = {
        "Intra-EU27": "#1f77b4",      # 파란색 (EU 역내)
        "Extra-EU27": "#17becf",      # 청록색 (EU 역외 유럽)
        "Europe": "#1f77b4",          # 파란색 (기본)
        "Africa": "#ff7f0e",          # 주황색
        "Middle East": "#2ca02c",     # 녹색
        "East Asia": "#d62728",       # 빨간색
        "Southeast Asia": "#9467bd",  # 보라색
        "North America": "#8c564b",   # 갈색
        "Central/South America": "#e377c2",  # 분홍색
        "Oceania": "#7f7f7f",         # 회색
        "Others": "#bcbd22"           # 올리브색
    }
    
    # 노드 색상 및 폰트 색상 설정
    node_colors = []
    font_colors = []
    for node in all_nodes:
        if node in reporters_display:
            node_colors.append(reporter_color)
            font_colors.append(reporter_font_color)
        elif node in cmdcodes_prefixed:
            # HS Code 노드 (cmdcodes_prefixed에 포함된 모든 노드)
            node_colors.append(hscode_color)
            font_colors.append(hscode_font_color)
        else:
            # Partner 노드 (대륙 체크)
            matched_continent = False
            for continent_name, continent_color in continent_colors.items():
                if node.startswith(continent_name):
                    node_colors.append(continent_color)
                    font_colors.append(partner_font_color)
                    matched_continent = True
                    break
            if not matched_continent:
                node_colors.append(partner_color)
                font_colors.append(partner_font_color)
    
    # 링크 색상 (회색 + 투명도)
    link_color = f'rgba(100, 100, 100, {link_opacity})'
    
    # Sankey 다이어그램 생성 (Plotly Sankey는 노드별 폰트 색상 미지원)
    fig = go.Figure(data=[go.Sankey(
        textfont=dict(size=font_size, color=reporter_font_color),
        node=dict(
            pad=15,
            thickness=node_thickness,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_color
        )
    )])
    
    # Sankey 다이어그램 노드를 드래그 가능하게 설정
    fig.update_traces(
        arrangement='freeform'  # 노드를 자유롭게 드래그하여 재배치 가능
    )
    
    fig.update_layout(
        title_text=custom_title,
        font=dict(
            size=font_size,
            family="Arial, sans-serif",
            color=reporter_font_color
        ),
        height=diagram_height,
        xaxis={'showgrid': False, 'zeroline': False, 'visible': False},
        yaxis={'showgrid': False, 'zeroline': False, 'visible': False},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig


def get_all_countries_list():
    """
    COUNTRIES_BY_REGION에서 모든 국가를 평면 리스트로 추출
    
    Returns:
        country_options: [(display_name, code), ...] 형식의 리스트
    """
    country_options = []
    
    def extract_countries(data, region_name=""):
        """재귀적으로 국가 코드 추출"""
        if isinstance(data, list):
            # 리스트인 경우: 국가 코드 목록
            for code in data:
                country_name = COUNTRY_NAMES.get(code, f"Unknown ({code})")
                display_name = f"{country_name} ({code})"
                if region_name:
                    display_name = f"[{region_name}] {display_name}"
                country_options.append((display_name, code))
        elif isinstance(data, dict):
            # 딕셔너리인 경우: 하위 지역 재귀 처리
            for key, value in data.items():
                extract_countries(value, key)
    
    # 모든 지역 처리
    for region_name, sub_regions in COUNTRIES_BY_REGION.items():
        extract_countries(sub_regions, region_name)
    
    # 중복 제거 및 정렬 (국가명 기준)
    country_options = list(set(country_options))
    country_options.sort(key=lambda x: x[0])
    
    return country_options




# ─────────────────────────────────────────────
# 웹페이지 UI — Tableau/Metabase Light Theme
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Comtrade Downloader",
    layout="wide"
)

# ── Tableau/Metabase Light CSS ─────────────────
st.markdown("""
<style>
/* ─── 전체 배경: 연한 블루-그레이 ─── */
.stApp { background-color: #F0F4F8; }
.main .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

/* ─── 기본 텍스트: 다크 슬레이트 (배경 대비 14:1 이상) ─── */
body, p, label, span, div, h1, h2, h3 { color: #1C2537; }

/* ─── 사이드바: 라이트 실버 (메인과 통일) ─── */
section[data-testid="stSidebar"] {
    background-color: #EEF2F7 !important;
    border-right: 1px solid #DCE3ED !important;
}
section[data-testid="stSidebar"] > div:first-child {
    background-color: #EEF2F7 !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] .stMarkdown {
    color: #1C2537 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #DCE3ED !important;
}
/* 사이드바 위젯 */
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"],
section[data-testid="stSidebar"] .stTextInput input {
    background-color: #FFFFFF !important;
    border-color: #C8D3DF !important;
    color: #1C2537 !important;
}

/* ─── 메인 위젯 ─── */
.stSelectbox [data-baseweb="select"],
.stMultiSelect [data-baseweb="select"],
.stTextInput input,
.stFileUploader {
    background-color: #FFFFFF !important;
    border-color: #C8D3DF !important;
    color: #1C2537 !important;
}
/* 드롭다운 리스트 */
[data-baseweb="popover"], [data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    border-color: #C8D3DF !important;
    color: #1C2537 !important;
}
[data-baseweb="menu"] li { color: #1C2537 !important; }
/* selectbox 선택 값 */
[data-baseweb="select"] span { color: #1C2537 !important; }
/* multiselect 태그 */
[data-baseweb="tag"] { background-color: #E4EBF5 !important; }
[data-baseweb="tag"] span { color: #1C2537 !important; }

/* ─── Primary 버튼: Tableau 오렌지 ─── */
.stButton > button[kind="primary"] {
    background-color: #F28E2B !important;
    border-color: #F28E2B !important;
    color: #FFFFFF !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: 10px 24px !important;
    width: 100% !important;
    letter-spacing: 0.3px !important;
    transition: background-color 0.18s ease, box-shadow 0.18s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #D4761E !important;
    border-color: #D4761E !important;
    box-shadow: 0 2px 8px rgba(242,142,43,0.30) !important;
}

/* ─── 다운로드 버튼 ─── */
.stDownloadButton > button {
    background-color: transparent !important;
    border: 2px solid #F28E2B !important;
    color: #F28E2B !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: all 0.18s ease !important;
}
.stDownloadButton > button:hover {
    background-color: #F28E2B !important;
    color: #FFFFFF !important;
}

/* ─── 진행바: Tableau 오렌지 ─── */
div[data-testid="stProgress"] > div > div > div {
    background-color: #F28E2B !important;
}
div[data-testid="stProgress"] > div > div {
    background-color: #DCE3ED !important;
}

/* ─── 데이터프레임 ─── */
.stDataFrame {
    border-radius: 8px !important;
    overflow: hidden;
    border: 1px solid #DCE3ED !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* ─── Metric 카드 ─── */
div[data-testid="metric-container"] {
    background-color: #FFFFFF !important;
    border: 1px solid #DCE3ED !important;
    border-top: 3px solid #F28E2B !important;
    border-radius: 8px;
    padding: 16px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
div[data-testid="metric-container"] label {
    color: #5E6E82 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    color: #1C2537 !important;
    font-size: 24px !important;
    font-weight: 700 !important;
}

/* ─── Expander ─── */
details {
    background-color: #FFFFFF !important;
    border: 1px solid #DCE3ED !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
details > summary {
    font-weight: 600 !important;
    color: #1C2537 !important;
    padding: 10px 14px !important;
}

/* ─── 알림 메시지 ─── */
div[data-testid="stAlert"] { border-radius: 8px !important; }

/* ─── radio / checkbox 라벨 ─── */
.stRadio label, .stCheckbox label { color: #1C2537 !important; }

/* ─── caption ─── */
.stCaptionContainer { color: #5E6E82 !important; }

/* ─── 파일 업로더 ─── */
[data-testid="stFileUploader"] {
    background-color: #FFFFFF !important;
    border: 1px dashed #C8D3DF !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


def section_header(num, title):
    st.markdown(
        f"<div style='display:flex;align-items:center;margin-bottom:10px;padding-bottom:8px;"
        f"border-bottom:2px solid #DCE3ED;'>"
        f"<span style='display:inline-flex;align-items:center;justify-content:center;"
        f"width:26px;height:26px;background:#2C3E50;color:#FFFFFF;border-radius:4px;"
        f"font-weight:700;font-size:13px;margin-right:10px;flex-shrink:0;'>{num}</span>"
        f"<span style='font-size:17px;font-weight:700;color:#1C2537;'>{title}</span></div>",
        unsafe_allow_html=True
    )


def accent_divider():
    st.markdown(
        "<div style='height:2px;background:linear-gradient(to right,#F28E2B,#509EE3,transparent);"
        "border-radius:2px;margin:20px 0;'></div>",
        unsafe_allow_html=True
    )


# ── 타이틀 ───────────────────────────────────
st.markdown(
    "<div style='padding:10px 0 4px 0;'>"
    "<h1 style='color:#1C2537;font-size:28px;font-weight:800;margin:0 0 4px 0;"
    "letter-spacing:-0.5px;'>Comtrade Downloader</h1>"
    "<p style='color:#5E6E82;font-size:14px;margin:0;'>UN Comtrade API 기반 국제무역 데이터 수집 도구</p>"
    "<div style='text-align:right;margin-top:-34px;color:#8A9BB0;font-size:12px;'>Myeong suhwan</div>"
    "</div>",
    unsafe_allow_html=True
)
accent_divider()

st.markdown(
    "<p style='color:#5E6E82;font-size:14px;margin-bottom:20px;'>보고 국가와 상대국을 직접 선택하거나, "
    "<strong style='color:#F28E2B;'>EU 역외 교역</strong>을 자동 계산할 수 있습니다.</p>",
    unsafe_allow_html=True
)

# ── 사이드바 ──────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='color:#2C3E50;font-size:17px;font-weight:700;margin-bottom:8px;'>API 설정</div>",
        unsafe_allow_html=True
    )
    api_key = st.text_input("Subscription Key", type="password")

    st.markdown("<hr style='border-color:#DCE3ED;margin:14px 0;'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#2C3E50;font-size:14px;font-weight:700;margin-bottom:8px;'>교역 구분 (Flow)</div>",
        unsafe_allow_html=True
    )
    flow_options = st.multiselect(
        "수집할 항목:",
        ["수입 (Import)", "수출 (Export)"],
        default=["수입 (Import)"]
    )
    flow_codes = []
    if "수입 (Import)" in flow_options: flow_codes.append("M")
    if "수출 (Export)" in flow_options: flow_codes.append("X")
    final_flow_code = ",".join(flow_codes)

    st.markdown("<hr style='border-color:#DCE3ED;margin:14px 0;'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#2C3E50;font-size:14px;font-weight:700;margin-bottom:8px;'>다이어그램 설정</div>",
        unsafe_allow_html=True
    )

    theme_presets = {
        "기본 (Default)":      {"reporter": "#2E86AB", "hscode": "#A23B72", "partner": "#F18F01"},
        "다크 모드 (Dark)":    {"reporter": "#00D4FF", "hscode": "#FF6B6B", "partner": "#4ECDC4"},
        "파스텔 (Pastel)":     {"reporter": "#A8E6CF", "hscode": "#DDA0DD", "partner": "#FFD93D"},
        "비즈니스 (Business)": {"reporter": "#003366", "hscode": "#666666", "partner": "#CC6600"},
        "네온 (Neon)":         {"reporter": "#00FFFF", "hscode": "#FF00FF", "partner": "#FFFF00"},
    }

    selected_theme = st.selectbox("테마 선택:", list(theme_presets.keys()))
    theme_colors = theme_presets[selected_theme]

    with st.expander("세부 설정"):
        diagram_font_size = st.slider("폰트 크기", min_value=15, max_value=50, value=20)
        diagram_height    = st.slider("다이어그램 높이 (px)", min_value=400, max_value=1000, value=600, step=50)
        node_thickness    = st.slider("노드 두께", min_value=10, max_value=100, value=20, step=5)
        link_opacity      = st.slider("링크 투명도", min_value=0.1, max_value=0.8, value=0.3, step=0.1)

        st.caption("노드 색상")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            reporter_color = st.color_picker("Reporter", value=theme_colors["reporter"])
        with col_c2:
            hscode_color   = st.color_picker("HS Code",  value=theme_colors["hscode"])
        with col_c3:
            partner_color  = st.color_picker("Partner",  value=theme_colors["partner"])

        reporter_font_color = st.color_picker("폰트 색상 (레이블)", value="#1C2537")
        hscode_font_color   = reporter_font_color
        partner_font_color  = reporter_font_color

        st.caption("제목 설정")
        show_diagram_title = st.checkbox("제목 표시", value=True)
        if show_diagram_title:
            custom_title = st.text_input("제목 입력", value="Alluvial Diagram: Reporter → HS Code → Partner")
        else:
            custom_title = ""

        st.caption("비율 표시 (##.#%)")
        show_hscode_percentage  = st.checkbox("HS Code 비율 표시", value=False)
        show_partner_percentage = st.checkbox("Partner 비율 표시", value=False)

        st.caption("한글 변환")
        use_korean_labels = st.checkbox("한글명으로 표시", value=False,
                                        help="Reporter, HS Code, Partner를 한글명으로 변환")


# ── 메인 UI ───────────────────────────────────
col1, col2 = st.columns([1, 1])
all_countries = get_all_countries_list()

with col1:
    section_header("1", "보고 국가 (Reporter)")
    st.markdown("<p style='font-size:13px;font-weight:600;color:#5E6E82;margin-bottom:6px;'>빠른 선택 옵션</p>",
                unsafe_allow_html=True)
    reporter_quick_select = st.selectbox(
        "그룹 선택 (선택사항)",
        ["선택 안함"] + [k for k in REPORTER_GROUPS.keys() if k != "직접 입력 (Custom)"],
        key="reporter_quick_select"
    )

    if reporter_quick_select != "선택 안함":
        reporter_code = REPORTER_GROUPS[reporter_quick_select]
        display_code  = (reporter_code[:30] + "...") if len(reporter_code) > 30 else reporter_code
        st.caption(f"Code: {display_code}")
    else:
        st.markdown("<hr style='margin:10px 0;border-color:#DCE3ED;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:13px;font-weight:600;color:#5E6E82;margin-bottom:6px;'>개별 국가 선택 (검색 가능)</p>",
                    unsafe_allow_html=True)
        selected_reporters = st.multiselect(
            "국가를 선택하세요",
            options=[display for display, code in all_countries],
            default=[],
            key="reporter_multiselect",
            help="국가명이나 코드로 검색할 수 있습니다"
        )
        selected_reporter_codes = [code for display, code in all_countries if display in selected_reporters]
        reporter_code = ",".join(selected_reporter_codes) if selected_reporter_codes else ""
        if selected_reporter_codes:
            st.markdown(
                f"<div style='background:#EBF7F2;border-left:3px solid #59A14F;padding:8px 12px;"
                f"border-radius:0 6px 6px 0;font-size:13px;color:#2E7D32;font-weight:600;'>"
                f"{len(selected_reporter_codes)}개 국가 선택됨</div>",
                unsafe_allow_html=True
            )

selected_top_n = 5  # 기본값 (🔝 미선택 시 무시)

with col2:
    section_header("2", "상대국 (Partner)")
    st.markdown("<p style='font-size:13px;font-weight:600;color:#5E6E82;margin-bottom:6px;'>빠른 선택 옵션</p>",
                unsafe_allow_html=True)
    quick_select = st.selectbox(
        "그룹 선택 (선택사항)",
        ["선택 안함"] + [k for k in PARTNER_GROUPS.keys()
                        if k not in ["직접 입력 (Custom)", "--- 대륙별 선택 ---", "--- 기존 선택 ---"]],
        key="partner_quick_select"
    )

    if quick_select != "선택 안함" and quick_select not in ["--- 대륙별 선택 ---", "--- 기존 선택 ---"]:
        partner_code_val = PARTNER_GROUPS[quick_select]
        if quick_select.startswith("🔝"):
            selected_top_n = st.number_input(
                "상위 국가 수 (N):", min_value=1, max_value=30, value=5, step=1,
                key="top_n_input",
                help="물량(kg) 기준 상위 N개국을 표시하고, 나머지는 '기타'로 합산합니다."
            )
            st.markdown(
                f"<div style='background:#FFF8EF;border-left:3px solid #F28E2B;padding:8px 12px;"
                f"border-radius:0 6px 6px 0;font-size:13px;color:#D4761E;'>"
                f"물량 기준 상위 <b>{int(selected_top_n)}개국</b> 표시, 나머지 기타 통합</div>",
                unsafe_allow_html=True
            )
            partner_code_val = "0"
        else:
            display_code = (partner_code_val[:30] + "...") if len(partner_code_val) > 30 else partner_code_val
            st.caption(f"Code: {display_code}")
    else:
        st.markdown("<hr style='margin:10px 0;border-color:#DCE3ED;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:13px;font-weight:600;color:#5E6E82;margin-bottom:6px;'>개별 국가 선택 (검색 가능)</p>",
                    unsafe_allow_html=True)
        selected_partners = st.multiselect(
            "국가를 선택하세요",
            options=[display for display, code in all_countries],
            default=[],
            key="partner_multiselect",
            help="국가명이나 코드로 검색할 수 있습니다"
        )
        selected_partner_codes = [code for display, code in all_countries if display in selected_partners]
        partner_code_val = ",".join(selected_partner_codes) if selected_partner_codes else ""
        if selected_partner_codes:
            st.markdown(
                f"<div style='background:#EBF7F2;border-left:3px solid #59A14F;padding:8px 12px;"
                f"border-radius:0 6px 6px 0;font-size:13px;color:#2E7D32;font-weight:600;'>"
                f"{len(selected_partner_codes)}개 국가 선택됨</div>",
                unsafe_allow_html=True
            )


accent_divider()
section_header("3", "연도 및 품목")

col3, col4 = st.columns([2, 1])
with col3:
    uploaded_file = st.file_uploader("HS 코드 파일 (CSV/TXT)", type=["csv", "txt"])

    with st.expander("또는 HS 코드 직접 선택 (콤보박스)"):
        hs_digit = st.radio(
            "HS 자릿수:",
            ["2자리 (챕터)", "4자리 (헤딩)", "6자리 (소호)"],
            horizontal=True,
            key="hs_digit_level"
        )
        if hs_digit == "2자리 (챕터)":
            hs_options = [f"{k} | {v}" for k, v in HS2_CODES.items()]
        elif hs_digit == "4자리 (헤딩)":
            hs_options = [f"{k} | {v}" for k, v in HS4_CODES.items()]
        else:
            hs_options = [f"{k} | {v}" for k, v in HS6_CODES.items()]

        selected_hs_combo = st.multiselect(
            "HS 코드 선택:",
            hs_options,
            placeholder="코드 또는 품목명으로 검색...",
            key="hs_combo_select"
        )
        if selected_hs_combo:
            preview = [opt.split(" | ")[0] for opt in selected_hs_combo]
            st.caption(f"{len(preview)}개 선택됨: {', '.join(preview)}")

with col4:
    selected_years = st.multiselect("연도 선택:", YEAR_OPTIONS, default=["2023"])


accent_divider()
section_header("4", "다운로드 형식")
download_format = st.radio(
    "파일 형식:",
    ["CSV (쉼표 구분)", "TSV (탭 구분)"],
    horizontal=True,
    key="download_format"
)


# ── 수집 버튼 ─────────────────────────────────
st.markdown("<div style='margin:24px 0 8px;'>", unsafe_allow_html=True)
if st.button("데이터 수집 시작", type="primary"):
    has_hs_input = (uploaded_file is not None) or (len(selected_hs_combo) > 0)
    if not api_key or not has_hs_input or not final_flow_code:
        st.warning("설정 정보를 모두 입력해주세요. (HS 코드: 파일 업로드 또는 직접 선택 필요)")
    elif not reporter_code:
        st.error("Reporter 국가를 최소 1개 이상 선택해주세요.")
    elif not partner_code_val:
        st.error("Partner 국가를 선택하거나 빠른 선택 옵션을 사용해주세요.")
    else:
        hs_from_file = []
        if uploaded_file:
            if uploaded_file.name.endswith(".csv"):
                df_input     = pd.read_csv(uploaded_file, dtype=str)
                hs_from_file = df_input.iloc[:, 0].dropna().tolist()
            else:
                stringio     = uploaded_file.getvalue().decode("utf-8")
                hs_from_file = [line.strip() for line in stringio.split("\n") if line.strip()]

        hs_from_combo     = [opt.split(" | ")[0].strip() for opt in selected_hs_combo]
        hs_codes          = hs_from_file + hs_from_combo
        original_hs_codes = [c for c in hs_codes if c]
        hs_codes          = list(set(original_hs_codes))

        if quick_select and quick_select.startswith("🔝"):
            short_hs_codes = [hs for hs in hs_codes if len(str(hs).strip()) < 4]
            if short_hs_codes:
                st.warning(
                    f"HS 2자리 코드 감지: {', '.join(short_hs_codes[:3])}"
                    f"{'...' if len(short_hs_codes) > 3 else ''} — "
                    f"상위 N개국 분석은 HS 4자리 이상에서 더 정확합니다."
                )

        target_years   = sorted(selected_years, reverse=True)
        reporters_list = ([r.strip() for r in reporter_code.split(",") if r.strip()]
                          if "," in reporter_code else [reporter_code])
        total_tasks    = len(hs_codes) * len(target_years) * len(reporters_list)

        st.markdown(
            f"<div style='background:#FFFFFF;border:1px solid #DCE3ED;border-left:4px solid #F28E2B;"
            f"border-radius:6px;padding:12px 16px;margin:12px 0;'>"
            f"<span style='color:#D4761E;font-weight:700;font-family:monospace;'>"
            f"총 {total_tasks}회 API 요청 예정</span></div>",
            unsafe_allow_html=True
        )

        all_data     = []
        progress_bar = st.progress(0)
        status_text  = st.empty()
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

        status_text.text("완료!")

        if all_data:
            final_df              = pd.concat(all_data, ignore_index=True)
            final_df_preprocessed = preprocess_dataframe(final_df, original_hs_codes)
            final_df, dedup_report = remove_duplicates_with_report(final_df_preprocessed)

            c_a, c_b, c_c = st.columns(3)
            with c_a: st.metric("수집 건수", f"{len(final_df):,}")
            with c_b: st.metric("HS 코드 수", len(hs_codes))
            with c_c: st.metric("연도 수", len(target_years))

            if dedup_report["duplicates_removed"] > 0:
                st.warning(
                    f"중복 제거 완료: {dedup_report['original_count']:,} 건 → "
                    f"{dedup_report['cleaned_count']:,} 건 (중복 {dedup_report['duplicates_removed']:,} 건 제거)"
                )
                if dedup_report["reporter_duplicates"]:
                    with st.expander("Reporter별 중복 제거 상세"):
                        st.caption("완전히 동일한 행만 제거되었습니다.")
                        for rc, stats in sorted(dedup_report["reporter_duplicates"].items(),
                                                key=lambda x: x[1]["removed"], reverse=True):
                            rn = COUNTRY_NAMES.get(rc, "") or COUNTRY_NAMES_ENG.get(rc, rc)
                            st.write(f"**{rn} ({rc})**: {stats['before']:,} → {stats['after']:,} 건 "
                                     f"(중복 {stats['removed']:,} 건 제거)")
            else:
                st.success(f"수집 성공!  총 {len(final_df):,} 건 (중복 없음)")

            st.dataframe(final_df.head(), use_container_width=True)

            # HS Code 한글명 추가 (동적 DB 기반)
            final_df_download = final_df.copy()
            if "cmdCode" in final_df_download.columns:
                hs_kor_map = {k: v.split("(")[0].strip() for k, v in {**HS2_CODES, **HS4_CODES, **HS6_CODES}.items()}
                final_df_download["cmdCodeKor"] = final_df_download["cmdCode"].astype(str).map(hs_kor_map).fillna("")
                cols = list(final_df_download.columns)
                cols.remove("cmdCodeKor")
                if "cmdCode" in cols:
                    cols.insert(cols.index("cmdCode") + 1, "cmdCodeKor")
                final_df_download = final_df_download[cols]

            safe_ptn = "Custom" if quick_select == "선택 안함" else quick_select.split("(")[0].strip()
            if "CSV" in download_format:
                file_data    = final_df_download.to_csv(index=False, encoding="utf-8-sig")
                file_name    = f"TradeData_{safe_ptn}_{target_years[0]}.csv"
                mime_type    = "text/csv"
                button_label = "결과 다운로드 (CSV)"
            else:
                file_data    = final_df_download.to_csv(index=False, sep="\t", encoding="utf-8-sig")
                file_name    = f"TradeData_{safe_ptn}_{target_years[0]}.tsv"
                mime_type    = "text/tab-separated-values"
                button_label = "결과 다운로드 (TSV)"

            st.download_button(label=button_label, data=file_data, file_name=file_name, mime=mime_type)

            st.session_state["final_df"]             = final_df
            st.session_state["partner_mode"]         = partner_code_val
            st.session_state["saved_reporter_group"] = reporter_quick_select
            st.session_state["quick_select"]         = quick_select
            if quick_select and quick_select.startswith("🔝"):
                st.session_state["selected_top_n"] = int(selected_top_n)
        else:
            st.markdown(
                "<div style='background:#FFF8EF;border-left:3px solid #F28E2B;padding:12px 16px;"
                "border-radius:0 8px 8px 0;color:#D4761E;'>데이터가 없습니다. 조건을 확인해주세요.</div>",
                unsafe_allow_html=True
            )
st.markdown("</div>", unsafe_allow_html=True)


# ── Alluvial Diagram ──────────────────────────
if "final_df" in st.session_state and not st.session_state["final_df"].empty:
    accent_divider()
    section_header("5", "Alluvial Diagram")
    st.caption("Reporter → HS Code → Partner  |  두께: 물량(kg) 기준")

    partner_mode         = st.session_state.get("partner_mode", "")
    group_by_continent   = (partner_mode == "ALL_CONTINENTS")
    saved_reporter_group = st.session_state.get("saved_reporter_group", "")
    merge_eu27           = (saved_reporter_group == "EU 27 전체 (All EU Members)")
    saved_quick_select   = st.session_state.get("quick_select", "")
    is_topn_mode      = saved_quick_select.startswith("🔝")
    is_all_individual = (st.session_state.get("partner_mode") == "all")
    saved_top_n       = st.session_state.get("selected_top_n", 5)
    top_n = saved_top_n if is_topn_mode else (10 if is_all_individual else None)

    try:
        fig = create_alluvial_diagram(
            st.session_state["final_df"],
            font_size=diagram_font_size,
            reporter_color=reporter_color,
            hscode_color=hscode_color,
            partner_color=partner_color,
            reporter_font_color=reporter_font_color,
            hscode_font_color=hscode_font_color,
            partner_font_color=partner_font_color,
            link_opacity=link_opacity,
            diagram_height=diagram_height,
            node_thickness=node_thickness,
            group_by_continent=group_by_continent,
            custom_title=custom_title,
            merge_eu27_reporter=merge_eu27,
            show_hscode_percentage=show_hscode_percentage,
            show_partner_percentage=show_partner_percentage,
            top_n_partners=top_n,
            use_korean_labels=use_korean_labels
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="main_diagram")
        else:
            st.info("다이어그램을 생성할 데이터가 충분하지 않습니다. (물량 데이터 필요)")
    except Exception as e:
        st.error(f"다이어그램 생성 오류: {e}")

# ── 동향 보고서 ────────────────────────────────
if "final_df" in st.session_state and not st.session_state["final_df"].empty:
    accent_divider()
    section_header("6", "동향 보고서")
    st.caption("조회된 데이터의 주요 수치 및 특징을 자동으로 요약합니다.")
    try:
        report_html = generate_trend_report(st.session_state["final_df"])
        if report_html:
            st.markdown(report_html, unsafe_allow_html=True)
        else:
            st.info("보고서를 생성할 데이터가 없습니다.")
    except Exception as e:
        st.error(f"보고서 생성 오류: {e}")
