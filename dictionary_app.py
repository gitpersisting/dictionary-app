
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

# 词汇联想下拉框（双列）
all_words = load_word_list()
col1, col2 = st.columns(2)

with col1:
    word1 = st.selectbox("🔎 单词搜索框 1", all_words, key="box1")

with col2:
    word2 = st.selectbox("🔎 单词搜索框 2", all_words, key="box2")

# 你可以修改为从 word2 读取，或添加逻辑判断
word = word1

# 查询函数
def query_word(w):
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dictionary WHERE word = ?", (w,))
    row = cursor.fetchone()
    conn.close()
    return row

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
else:
    st.info("请选择或输入一个单词进行查询。")
