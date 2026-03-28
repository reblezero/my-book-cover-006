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
                # 실제 검색된 책 제목 추출
                title_tag = box.select_one("a.bo3 b")
                if title_tag:
                    final_title = title_tag.get_text().strip()
                break
        
        if not img_src: return None, None
        
        # [화질 개선 핵심] 주소에서 숫자를 바꿔 고화질 원본 요청
        # coversum -> cover500 (가장 큰 사이즈)
        high_res_src = img_src.replace('coversum', 'cover500').replace('cover200', 'cover500').replace('cover150', 'cover500')
        
        img_res = requests.get(high_res_src, headers=headers, verify=False, timeout=10)
        img = Image.open(BytesIO(img_res.content))
        
        return img, final_title
    except Exception:
        return None, None

# --- 웹 화면(UI) 구성 ---
st.set_page_config(page_title="고화질 표지 개별 수집기", page_icon="🖼️")
st.title("🖼️ 고화질 표지 개별 수집기")
st.markdown("책 제목을 입력하면 **원본급 고화질** 이미지를 책별로 따로따로 보여줍니다.")

titles_input = st.text_area("책 제목 (한 줄에 하나씩):", height=150, placeholder="구름 사람들\n파친코")

if st.button("🚀 고화질 표지 찾기"):
    titles = [t.strip() for t in titles_input.split('\n') if t.strip()]
    if not titles:
        st.warning("제목을 입력해주세요!")
    else:
        st.info("고화질 이미지를 불러오는 중입니다. 잠시만 기다려주세요...")
        
        # 각 책별로 결과를 출력하기 위해 루프를 돌립니다.
        for t in titles:
            img, book_name = get_high_res_cover(t)
            
            if img:
                with st.container():
                    st.divider()
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # 화면에 고화질 미리보기 표시
                        st.image(img, use_container_width=True)
                    
                    with col2:
                        st.subheader(f"📖 {book_name}")
                        st.write(f"해상도: {img.width} x {img.height}")
                        
                        # JPG로 변환하여 다운로드 버튼 생성
                        buf = BytesIO()
                        img.convert("RGB").save(buf, format="JPEG", quality=100) # 최고 품질
                        byte_im = buf.getvalue()
                        
                        st.download_button(
                            label=f"📥 '{book_name}' JPG 다운로드",
                            data=byte_im,
                            file_name=f"{book_name}_{datetime.now().strftime('%H%M%S')}.jpg",
                            mime="image/jpeg",
                            key=f"btn_{book_name}_{datetime.now().timestamp()}" # 고유 키 생성
                        )
            else:
                st.error(f"❌ '{t}' : 표지를 찾을 수 없습니다.")