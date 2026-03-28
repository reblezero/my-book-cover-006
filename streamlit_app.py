import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import urllib.parse
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# --- 핵심 기능: 알라딘에서 '진짜' 고화질 표지 가져오기 ---
def get_high_res_cover(book_title):
    try:
        encoded_title = urllib.parse.quote(book_title)
        url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&SearchWord={encoded_title}"
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.aladin.co.kr/"}
        
        res = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        boxes = soup.select("div.ss_book_box")
        
        img_src = None
        final_title = book_title
        
        for box in boxes:
            box_text = box.get_text()
            if any(x in box_text for x in ["[알라딘 굿즈]", "[음반]", "머그", "[블루레이]"]):
                continue 
            
            img_tag = box.select_one("img.i_cover") or box.select_one("img.front_cover")
            if img_tag and img_tag.has_attr('src'):
                img_src = img_tag['src']
                title_tag = box.select_one("a.bo3 b")
                if title_tag:
                    final_title = title_tag.get_text().strip()
                break
        
        if not img_src: return None, None
        
        # 고화질 치환 (cover500)
        high_res_src = img_src.replace('coversum', 'cover500').replace('cover200', 'cover500').replace('cover150', 'cover500')
        img_res = requests.get(high_res_src, headers=headers, verify=False, timeout=10)
        img = Image.open(BytesIO(img_res.content))
        
        # 이미지 데이터를 바이트로 미리 변환 (세션 저장을 위해)
        buf = BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=100)
        return buf.getvalue(), final_title
    except Exception:
        return None, None

# --- UI 및 세션 관리 ---
st.set_page_config(page_title="고화질 표지 수집기", page_icon="🖼️")
st.title("🖼️ 고화질 표지 개별 수집기")
st.markdown("다운로드 버튼을 눌러도 검색 결과가 사라지지 않습니다!")

# 검색 결과를 저장할 세션 초기화
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

titles_input = st.text_area("책 제목 (한 줄에 하나씩):", height=150, placeholder="구름 사람들\n파친코")

if st.button("🚀 고화질 표지 찾기"):
    titles = [t.strip() for t in titles_input.split('\n') if t.strip()]
    if not titles:
        st.warning("제목을 입력해주세요!")
    else:
        results = []
        progress_bar = st.progress(0)
        for i, t in enumerate(titles):
            img_bytes, book_name = get_high_res_cover(t)
            if img_bytes:
                results.append({"name": book_name, "data": img_bytes})
            else:
                st.toast(f"❌ '{t}' 찾기 실패")
            progress_bar.progress((i + 1) / len(titles))
        
        # 세션에 결과 저장
        st.session_state.search_results = results

# --- 결과 출력 영역 (세션에 저장된 데이터를 뿌려줌) ---
if st.session_state.search_results:
    st.success(f"총 {len(st.session_state.search_results)}권의 표지를 찾았습니다.")
    for idx, item in enumerate(st.session_state.search_results):
        with st.container():
            st.divider()
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(item['data'], use_container_width=True)
            
            with col2:
                st.subheader(f"📖 {item['name']}")
                st.download_button(
                    label=f"📥 JPG 다운로드",
                    data=item['data'],
                    file_name=f"{item['name']}.jpg",
                    mime="image/jpeg",
                    key=f"btn_{idx}_{item['name']}" # 인덱스를 넣어 고유 키 보장
                )