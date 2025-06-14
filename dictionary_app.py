import streamlit as st
import sqlite3
import json

st.set_page_config(page_title="词典查询", page_icon="📚", layout="wide")
st.title("📖 英语词典查询工具")

# 从数据库加载所有单词
@st.cache_data
def load_word_list():
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM dictionary ORDER BY word")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

all_words = load_word_list()

# 用户输入关键词（不是 selectbox）
input_text = st.text_input("🔎 输入单词开头进行联想搜索：")

# 匹配前缀（忽略大小写）
suggestions = [w for w in all_words if w.lower().startswith(input_text.lower())] if input_text else []
suggestions = suggestions[:10]  # 限制最多展示10个

selected_word = None

# 如果有建议词，展示为双列按钮
if suggestions:
    st.markdown("### 🧠 联想词建议（点击查询）：")
    col1, col2 = st.columns(2)
    for i in range(5):
        left = suggestions[i] if i < len(suggestions) else None
        right = suggestions[i + 5] if i + 5 < len(suggestions) else None
        with col1:
            if left and st.button(f"👉 {left}", key=f"sug_left_{i}"):
                selected_word = left
        with col2:
            if right and st.button(f"👉 {right}", key=f"sug_right_{i}"):
                selected_word = right

# 如果用户点击了建议词，则进行查询
if selected_word:
    word = selected_word
else:
    word = None

# 查询数据库
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
elif input_text:
    st.info("请选择上方建议词进行查询。")
