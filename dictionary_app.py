import streamlit as st
import sqlite3
import json

st.set_page_config(page_title="词典查询", page_icon="📚", layout="wide")
st.title("📖 英语词典查询工具")

# 从数据库读取所有单词（仅加载一次）
@st.cache_data
def load_word_list():
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM dictionary")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

all_words = load_word_list()

# 文本输入 + 动态过滤
user_input = st.text_input("请输入单词前缀以联想：")

# 获取匹配词（最多5条）
matches = []
if user_input:
    matches = [w for w in all_words if w.lower().startswith(user_input.lower())][:5]

# 提示用户选择匹配项
selected_word = None
if matches:
    selected_word = st.selectbox("从联想结果中选择：", matches)
else:
    st.info("请输入至少一个字母以开始联想（最多显示5条匹配）")

# 查询数据库
def query_word(w):
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dictionary WHERE word = ?", (w,))
    row = cursor.fetchone()
    conn.close()
    return row

# 显示查询结果
if selected_word:
    result = query_word(selected_word)
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
