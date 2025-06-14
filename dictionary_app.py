import streamlit as st
import sqlite3
import json

st.set_page_config(page_title="词典查询", page_icon="📚", layout="wide")
st.title("📖 英语词典查询工具")

# 从数据库读取所有单词（用于下拉自动联想）
@st.cache_data
def load_word_list():
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM dictionary ORDER BY word")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

# 联想搜索框（单列、带下拉建议）
all_words = load_word_list()
word = st.selectbox("请输入或选择单词（支持自动联想）", all_words)

# 查询数据库函数
def query_word(w):
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dictionary WHERE word = ?", (w,))
    row = cursor.fetchone()
    conn.close()
    return row

# 查询结果展示
if word:
    result = query_word(word)
    if result:
        (
            word, pron_uk, pron_us, meanings, etym_full,
            etym_origin, etym_parts, examples_en, examples_zh
        ) = result

        st.subheader(f"🔤 单词：{word}")
        st.markdown(f"**英式发音**：/{pron_uk}/　　**美式发音**：/{pron_us}/")

        st.markdown("### 📘 词义")
        st.markdown(meanings.replace("•", "👉"))

        st.markdown("### 🧬 词源")
        st.markdown(f"**简述**：{etym_origin}")
        with st.expander("🔍 查看详细词源结构"):
            st.markdown(etym_full)
            try:
                parts = json.loads(etym_parts)
                for p in parts:
                    st.markdown(f"- `{p.get('part')}`：{p.get('meaning')}  ({p.get('origin')})")
            except:
                st.markdown("（词源结构数据解析失败）")

        st.markdown("### 💬 例句")
        try:
            examples_en_list = json.loads(examples_en)
            examples_zh_list = json.loads(examples_zh)
            for en, zh in zip(examples_en_list, examples_zh_list):
                st.markdown(f"- {en}  \n　👉 {zh}")
        except:
            st.markdown("例句格式错误")
    else:
        st.warning("未找到该单词，请检查拼写。")
