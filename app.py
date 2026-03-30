import os
import tempfile
import streamlit as st
from src.pipeline import run_pipeline, run_overlay_pipeline

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Nepali Doc Explainer",
    page_icon="📃",
    layout="centered"
)

st.title("📃 Nepali Document Explainer")
st.write("Upload a scanned nepali document and get a clear english explaination.")

uploaded_file = st.file_uploader(
    "Upload document image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Document", use_container_width=True)

    tab1, tab2 = st.tabs(["💡 Explain", "🔤 Translate Overlay"])

    with tab1:
        if st.button("Explain Document"):
            with st.spinner("Reading and explaining document..."):
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                tmp.write(uploaded_file.read())
                tmp.flush()
                tmp.close()
                tmp_path = tmp.name
        
                text, explanation = run_pipeline(tmp_path)
                os.unlink(tmp_path)

            if text:
                with st.expander("📃 Extracted Nepali Text"):
                    st.write(text)
                st.markdown("### 💡 Explanation")
                st.markdown(explanation)
            else:
                st.error(explanation)

    with tab2:
        if st.button("Translate Overlay"):
            with st.spinner("Translating lines by lines..."):
                uploaded_file.seek(0)
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                tmp.write(uploaded_file.read())
                tmp.flush()
                tmp.close()
                tmp_path = tmp.name

                result_img, error = run_overlay_pipeline(tmp_path)
                os.unlink(tmp_path)

            if error:
                st.error(error)
            elif result_img is not None:
                st.image(result_img, caption="Translated Document", width='stretch')
            else:
                st.error("Unexpected error: No image returned")