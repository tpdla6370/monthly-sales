import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="월별 매출집계 통합기", layout="centered")

st.title("📊 월별 매출집계 자동 통합기")
st.markdown("""
**[적용된 통합 규칙]**
1. 각 파일의 **첫 번째 시트**만 합칩니다.
2. **첫 번째 파일의 헤더(열 이름)**만 기준으로 사용합니다.
3. 중간 누락 없이 **마지막 행까지 전부 포함**하여 누적합니다.
""")

# 20~30개 파일 동시 업로드 창
uploaded_files = st.file_uploader(
    "여기에 엑셀 파일들을 한 번에 드래그 앤 드롭 하세요 (.xls, .xlsx 지원)", 
    type=["xls", "xlsx"], 
    accept_multiple_files=True
)

if uploaded_files:
    # 파일명 순서대로 정렬 (날짜 꼬임 방지)
    uploaded_files.sort(key=lambda x: x.name)
    st.info(f"총 {len(uploaded_files)}개의 파일이 대기 중입니다.")

    if st.button("🚀 엑셀 하나로 병합하기", type="primary"):
        combined_dfs = []
        base_columns = None
        
        progress_bar = st.progress(0)

        for idx, file in enumerate(uploaded_files):
            try:
                # 규칙 1: 첫 번째 시트만 읽기
                df = pd.read_excel(file, sheet_name=0)
                
                if df.empty:
                    continue
                
                # 규칙 2: 첫 파일의 헤더를 고정값으로 사용
                if base_columns is None:
                    base_columns = df.columns
                else:
                    # 두 번째 파일부터는 무조건 첫 번째 파일의 헤더명으로 덮어씌움
                    df.columns = base_columns
                
                # 규칙 3: 마지막 행까지 리스트에 누적
                combined_dfs.append(df)
            except Exception as e:
                st.error(f"오류 발생 ({file.name}): {e}")
                
            progress_bar.progress((idx + 1) / len(uploaded_files))

        if combined_dfs:
            # 전체 데이터 하나의 표로 병합
            final_df = pd.concat(combined_dfs, ignore_index=True)
            st.success(f"🎉 총 {len(final_df)}행 병합 완료! 아래 버튼을 눌러 다운로드하세요.")

            # 엑셀 바이너리 파일로 변환 (서버에 저장하지 않고 즉시 다운로드)
            excel_buffer = io.BytesIO()
            final_df.to_excel(excel_buffer, index=False, engine="openpyxl")
            excel_data = excel_buffer.getvalue()

            # 다운로드 버튼 생성
            st.download_button(
                label="📥 배송내역_최종통합.xlsx 다운로드",
                data=excel_data,
                file_name="배송내역_최종통합.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("합칠 유효한 데이터가 없습니다.")
