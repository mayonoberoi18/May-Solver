import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
import re
from datetime import datetime
import pytesseract
from PIL import Image
import cv2

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MaySolver OCR PRO MAX", layout="wide")

# 🔴 SET YOUR PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

x, y = sp.symbols('x y')

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- OCR PREPROCESS ----------------
def preprocess_image(image):
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # sharpen
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    sharp = cv2.filter2D(gray, -1, kernel)

    # threshold
    thresh = cv2.threshold(sharp, 0, 255,
                           cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    return thresh

# ---------------- OCR MULTI PASS ----------------
def extract_text_from_image(image):
    processed = preprocess_image(image)

    text1 = pytesseract.image_to_string(processed)
    text2 = pytesseract.image_to_string(image)

    # choose longer (usually better)
    text = text1 if len(text1) > len(text2) else text2

    return clean_ocr_text(text)

# ---------------- OCR CLEAN ----------------
def clean_ocr_text(text):
    text = text.lower()

    # fix common OCR mistakes
    text = text.replace("|", "1")
    text = text.replace("l", "1")
    text = text.replace("o", "0")

    text = re.sub(r'[^a-z0-9\s\+\-\*/=]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# ---------------- TEXT CLEAN ----------------
def clean(text):
    text = text.lower()
    text = text.replace("twice", "2 times")
    text = text.replace("thrice", "3 times")
    return text

# ---------------- RECTANGLE ----------------
def solve_rectangle(text):
    if "rectangle" not in text:
        return None

    steps = ["Let width = x"]
    width = x

    rel = re.search(r'(\d+).*more than.*width', text)
    if rel:
        length = width + int(rel.group(1))
        steps.append(f"Length = x + {int(rel.group(1))}")
    else:
        length = y

    half = re.search(r'half.*?(\d+)', text)
    full = re.search(r'perimeter.*?(\d+)', text)

    if half:
        p = 2 * int(half.group(1))
        steps.append(f"Half perimeter → {p}")
    elif full:
        p = int(full.group(1))
        steps.append(f"Perimeter = {p}")
    else:
        return None

    eq = sp.Eq(2 * (length + width), p)
    sol = sp.solve(eq, x)[0]

    return {
        "width": sol,
        "length": length.subs(x, sol),
        "equations": [eq],
        "steps": steps + ["Used: 2(L + W)"]
    }

# ---------------- ALGEBRA ----------------
def solve_algebra(text):
    nums = list(map(int, re.findall(r'\d+', text)))
    eqs = []

    if "sum" in text and nums:
        eqs.append(sp.Eq(x + y, nums[0]))

    if "difference" in text and nums:
        eqs.append(sp.Eq(x - y, nums[0]))

    if "product" in text and nums:
        eqs.append(sp.Eq(x * y, nums[0]))

    if eqs:
        sol = sp.solve(eqs, (x, y))
        return {
            "solution": sol,
            "equations": eqs,
            "steps": ["Solved algebra"]
        }

    return None

# ---------------- ENGINE ----------------
def smart_engine(text):
    text = clean(text)

    for solver in [solve_rectangle, solve_algebra]:
        res = solver(text)
        if res:
            return res

    return None

# ---------------- GRAPH ----------------
def plot_graph(eqs):
    fig = go.Figure()
    xs = np.linspace(-10, 10, 200)

    for eq in eqs:
        try:
            y_expr = sp.solve(eq, y)
            f = sp.lambdify(x, y_expr[0], "numpy")
            fig.add_trace(go.Scatter(x=xs, y=f(xs)))
        except:
            pass

    fig.update_layout(template="plotly_dark")
    return fig

# ---------------- UI ----------------
st.sidebar.title("🚀 MaySolver OCR PRO MAX")
page = st.sidebar.radio("Menu", ["Solver", "Image Solver", "Graph", "History"])

# -------- TEXT SOLVER --------
if page == "Solver":
    st.title("🧠 Text Solver")

    user_input = st.text_area("Enter problem:")

    if st.button("Solve"):
        result = smart_engine(user_input)

        if result:
            st.success("Solved!")

            if "equations" in result:
                for eq in result["equations"]:
                    st.latex(sp.latex(eq))

            for step in result["steps"]:
                st.write("•", step)

            st.subheader("Answer")
            for k,v in result.items():
                if k not in ["equations","steps"]:
                    st.write(f"{k} = {v}")

            st.session_state["eqs"] = result.get("equations", [])
        else:
            st.error("Could not understand")

# -------- IMAGE SOLVER --------
elif page == "Image Solver":
    st.title("📷 OCR PRO MAX")

    uploaded = st.file_uploader("Upload image", type=["png","jpg","jpeg"])

    if uploaded:
        image = Image.open(uploaded)
        st.image(image, use_container_width=True)

        if st.button("Extract & Solve"):
            text = extract_text_from_image(image)

            st.subheader("Extracted Text")
            st.write(text)

            result = smart_engine(text)

            if result:
                st.success("Solved!")

                if "equations" in result:
                    for eq in result["equations"]:
                        st.latex(sp.latex(eq))

                for step in result["steps"]:
                    st.write("•", step)

                st.subheader("Answer")
                for k,v in result.items():
                    if k not in ["equations","steps"]:
                        st.write(f"{k} = {v}")
            else:
                st.error("Could not understand extracted text")

# -------- GRAPH --------
elif page == "Graph":
    if "eqs" in st.session_state:
        st.plotly_chart(plot_graph(st.session_state["eqs"]))
    else:
        st.info("Solve something first")

# -------- HISTORY --------
elif page == "History":
    st.title("History")
    for item in st.session_state.history:
        st.write(item)

st.markdown("<center>🚀 OCR PRO MAX (Offline)</center>", unsafe_allow_html=True)
