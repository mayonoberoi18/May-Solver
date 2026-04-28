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
st.set_page_config(page_title="MaySolver AI", layout="wide")

# Windows Tesseract path (ignored on cloud)
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

x, y = sp.symbols('x y')

if "history" not in st.session_state:
    st.session_state.history = []

if "eqs" not in st.session_state:
    st.session_state.eqs = []

# ---------------- IMAGE PROCESS ----------------
def preprocess_image(image):
    img = image.convert("L")
    img = img.point(lambda p: 0 if p < 140 else 255)
    return np.array(img)

# ---------------- OCR ----------------
def ocr_multi_pass(image):
    img1 = preprocess_image(image)

    text1 = pytesseract.image_to_string(img1)
    text2 = pytesseract.image_to_string(image)

    resized = image.resize((image.width*2, image.height*2))
    text3 = pytesseract.image_to_string(resized)

    best = max([text1, text2, text3], key=len)
    return clean_ocr(best)

def clean_ocr(text):
    text = text.lower()

    replacements = {"|":"1","l":"1","o":"0","s":"5"}
    for k,v in replacements.items():
        text = text.replace(k,v)

    text = re.sub(r'[^a-z0-9\s\+\-\*/=]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# ---------------- MAIN SOLVER ----------------
def solve_ncert(text):
    text = text.lower()
    nums = list(map(int, re.findall(r'\d+', text)))

    # ---------- RECTANGLE ----------
    if any(w in text for w in ["rectangle","rectangular","garden","field"]):
        rel = re.search(r'(\d+).*?(more|greater|exceeds).*?width', text)
        half = re.search(r'half.*?perimeter.*?(\d+)', text)
        full = re.search(r'perimeter.*?(\d+)', text)

        if rel and (half or full):
            d = int(rel.group(1))
            p = 2*int(half.group(1)) if half else int(full.group(1))

            eq = sp.Eq(2*((x+d)+x), p)
            sol = sp.solve(eq, x)[0]

            return {
                "type":"Rectangle",
                "width": sol,
                "length": sol + d,
                "equations":[eq],
                "steps":[
                    "Let width = x",
                    f"Length = x + {d}",
                    f"Perimeter = {p}",
                    "Used 2(l + w)"
                ]
            }

    # ---------- AGE ----------
    if "age" in text and "sum" in text and "difference" in text:
        if len(nums)>=2:
            eq1 = sp.Eq(x+y, nums[0])
            eq2 = sp.Eq(x-y, nums[1])
            sol = sp.solve((eq1,eq2),(x,y))
            return {"type":"Age","solution":sol,"equations":[eq1,eq2]}

    # ---------- ALGEBRA ----------
    if "sum" in text and "difference" in text:
        if len(nums)>=2:
            eq1 = sp.Eq(x+y, nums[0])
            eq2 = sp.Eq(x-y, nums[1])
            sol = sp.solve((eq1,eq2),(x,y))
            return {"type":"Algebra","solution":sol,"equations":[eq1,eq2]}

    # ---------- SPEED ----------
    if "distance" in text and "time" in text and len(nums)>=2:
        return {
            "type":"Speed",
            "speed": nums[0]/nums[1],
            "steps":["Speed = Distance / Time"]
        }

    # ---------- DIRECT EQUATION ----------
    eq_match = re.findall(r'[\dx\+\-\*/= ]+', text)
    for e in eq_match:
        if "=" in e:
            try:
                expr = sp.sympify(e.replace("=", "-(")+")")
                sol = sp.solve(expr, x)
                return {
                    "type":"Equation",
                    "solution": sol,
                    "equations":[expr]
                }
            except:
                pass

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
st.sidebar.title("⚡ MaySolver AI")
page = st.sidebar.radio("Menu", ["Text Solver","Image Solver","Graph","History"])

# ---------- TEXT ----------
if page == "Text Solver":
    txt = st.text_area("Enter problem")

    if st.button("Solve"):
        res = solve_ncert(txt)

        if res:
            st.success(f"Solved ({res['type']})")

            if "equations" in res:
                st.session_state.eqs = res["equations"]
                for eq in res["equations"]:
                    st.latex(sp.latex(eq))

            if "steps" in res:
                for step in res["steps"]:
                    st.write("•", step)

            for k,v in res.items():
                if k not in ["steps","equations","type"]:
                    st.write(f"{k} = {v}")

            st.session_state.history.append({
                "time": str(datetime.now()),
                "input": txt,
                "result": res
            })

        else:
            st.error("Not understood")

# ---------- IMAGE ----------
elif page == "Image Solver":
    file = st.file_uploader("Upload image")

    if file:
        img = Image.open(file)
        st.image(img)

        if st.button("Solve Image"):
            text = ocr_multi_pass(img)

            st.subheader("Extracted Text")
            st.write(text)

            res = solve_ncert(text)

            if res:
                st.success(f"Solved ({res['type']})")

                if "equations" in res:
                    st.session_state.eqs = res["equations"]
                    for eq in res["equations"]:
                        st.latex(sp.latex(eq))

                if "steps" in res:
                    for step in res["steps"]:
                        st.write("•", step)

                for k,v in res.items():
                    if k not in ["steps","equations","type"]:
                        st.write(f"{k} = {v}")
            else:
                st.error("Could not solve")

# ---------- GRAPH ----------
elif page == "Graph":
    if st.session_state.eqs:
        st.plotly_chart(plot_graph(st.session_state.eqs))
    else:
        st.info("Solve something first")

# ---------- HISTORY ----------
elif page == "History":
    for h in st.session_state.history[::-1]:
        st.write("🕒", h["time"])
        st.write("Input:", h["input"])
        st.write("Result:", h["result"])
        st.markdown("---")
