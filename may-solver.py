import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
import pytesseract
from PIL import Image
import re
import os
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MaySolver ULTIMATE", layout="wide")

# Safe Tesseract path (ONLY for local Windows)
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

x, y = sp.symbols('x y')

if "history" not in st.session_state:
    st.session_state.history = []

if "eqs" not in st.session_state:
    st.session_state.eqs = []

# ---------------- IMAGE PROCESSING (NO CV2) ----------------
def preprocess_image(image):
    img = image.convert("L")  # grayscale

    # improve contrast (threshold)
    img = img.point(lambda p: 0 if p < 140 else 255)

    return np.array(img)

# ---------------- OCR ENGINE ----------------
def ocr_multi_pass(image):
    img1 = preprocess_image(image)

    text1 = pytesseract.image_to_string(img1)
    text2 = pytesseract.image_to_string(image)

    # resize (better detection)
    resized = image.resize((image.width*2, image.height*2))
    text3 = pytesseract.image_to_string(resized)

    texts = [text1, text2, text3]
    best = max(texts, key=len)

    return clean_ocr(best)

# ---------------- OCR CLEAN ----------------
def clean_ocr(text):
    text = text.lower()

    replacements = {
        "|":"1", "l":"1", "o":"0", "s":"5"
    }

    for k,v in replacements.items():
        text = text.replace(k,v)

    text = re.sub(r'[^a-z0-9\s\+\-\*/=]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# ---------------- NORMALIZE ----------------
def normalize(text):
    text = text.lower()
    text = text.replace("twice", "2 times")
    text = text.replace("thrice", "3 times")
    return text

# ---------------- RECTANGLE ----------------
def solve_rectangle(text):
    if "rectangle" not in text:
        return None

    width = x
    length = y
    steps = ["Let width = x"]

    rel = re.search(r'(\d+).*more than.*width', text)
    if rel:
        d = int(rel.group(1))
        length = x + d
        steps.append(f"Length = x + {d}")

    half = re.search(r'half.*?(\d+)', text)
    full = re.search(r'perimeter.*?(\d+)', text)

    if half:
        p = 2 * int(half.group(1))
    elif full:
        p = int(full.group(1))
    else:
        return None

    eq = sp.Eq(2*(length+width), p)
    sol = sp.solve(eq, x)[0]

    return {
        "width": sol,
        "length": length.subs(x, sol),
        "equations":[eq],
        "steps": steps + ["Used perimeter formula"]
    }

# ---------------- ALGEBRA ----------------
def solve_algebra(text):
    nums = list(map(int, re.findall(r'\d+', text)))
    eqs = []

    if "sum" in text and nums:
        eqs.append(sp.Eq(x+y, nums[0]))

    if "difference" in text and nums:
        eqs.append(sp.Eq(x-y, nums[0]))

    if "product" in text and nums:
        eqs.append(sp.Eq(x*y, nums[0]))

    if eqs:
        sol = sp.solve(eqs, (x,y))
        return {"solution": sol, "equations": eqs, "steps":["Solved algebra"]}

    return None

# ---------------- SPEED ----------------
def solve_speed(text):
    nums = list(map(int, re.findall(r'\d+', text)))

    if "distance" in text and "time" in text and len(nums)>=2:
        return {"speed": nums[0]/nums[1], "steps":["Speed = D/T"]}

    return None

# ---------------- ENGINE ----------------
def engine(text):
    text = normalize(text)

    for fn in [solve_rectangle, solve_speed, solve_algebra]:
        res = fn(text)
        if res:
            st.session_state.eqs = res.get("equations", [])
            st.session_state.history.append({
                "time": str(datetime.now()),
                "input": text,
                "result": res
            })
            return res

    return None

# ---------------- GRAPH ----------------
def plot_graph(eqs):
    fig = go.Figure()
    xs = np.linspace(-10,10,200)

    for eq in eqs:
        try:
            y_expr = sp.solve(eq, y)
            f = sp.lambdify(x, y_expr[0], "numpy")
            fig.add_trace(go.Scatter(x=xs, y=f(xs)))
        except:
            pass

    return fig

# ---------------- UI ----------------
st.sidebar.title("⚡ MaySolver ULTIMATE")
page = st.sidebar.radio("Menu", ["Text Solver","Image Solver","Graph","History"])

# TEXT
if page == "Text Solver":
    txt = st.text_area("Enter problem")
    if st.button("Solve"):
        res = engine(txt)
        if res:
            st.success("Solved")
            for eq in res.get("equations", []):
                st.latex(sp.latex(eq))
            for step in res.get("steps", []):
                st.write("•", step)
            for k,v in res.items():
                if k not in ["steps","equations"]:
                    st.write(f"{k} = {v}")
        else:
            st.error("Not understood")

# IMAGE
elif page == "Image Solver":
    file = st.file_uploader("Upload image")
    if file:
        img = Image.open(file)
        st.image(img)

        if st.button("Solve Image"):
            text = ocr_multi_pass(img)

            st.subheader("Extracted")
            st.write(text)

            res = engine(text)

            if res:
                st.success("Solved")
                for eq in res.get("equations", []):
                    st.latex(sp.latex(eq))
                for step in res.get("steps", []):
                    st.write("•", step)
                for k,v in res.items():
                    if k not in ["steps","equations"]:
                        st.write(f"{k} = {v}")
            else:
                st.error("Could not solve")

# GRAPH
elif page == "Graph":
    if st.session_state.eqs:
        st.plotly_chart(plot_graph(st.session_state.eqs))
    else:
        st.info("Solve something first")

# HISTORY
elif page == "History":
    for h in st.session_state.history[::-1]:
        st.write("🕒", h["time"])
        st.write("Input:", h["input"])
        st.write("Result:", h["result"])
        st.markdown("---")
