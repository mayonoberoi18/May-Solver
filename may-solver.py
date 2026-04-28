import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
import re
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MaySolver ENGINE MAX", layout="wide")

# ---------------- SYMBOLS ----------------
x, y = sp.symbols('x y')

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- PREPROCESS ----------------
def clean(text):
    text = text.lower()
    text = text.replace("twice", "2 times")
    text = text.replace("thrice", "3 times")
    return text

# ---------------- ENTITY EXTRACTION ----------------
def extract_entities(text):
    entities = {}
    if "width" in text: entities["width"] = x
    if "length" in text: entities["length"] = y
    if "age" in text: entities["age"] = x
    if "number" in text: entities["number"] = x
    return entities

# ---------------- RELATION EXTRACTION ----------------
def extract_relations(text):
    relations = []

    more = re.findall(r'(\d+).*more than.*(width|length|age|number)', text)
    for val, var in more:
        relations.append((var, "+", int(val)))

    less = re.findall(r'(\d+).*less than.*(width|length|age|number)', text)
    for val, var in less:
        relations.append((var, "-", int(val)))

    times = re.findall(r'(\d+)\s*times.*(number|age)', text)
    for val, var in times:
        relations.append((var, "*", int(val)))

    return relations

# ---------------- RECTANGLE ----------------
def solve_rectangle(text):
    if "rectangle" not in text:
        return None

    steps = ["Let width = x"]
    width = x
    length = y

    rel = re.search(r'(\d+).*more than.*width', text)
    if rel:
        diff = int(rel.group(1))
        length = width + diff
        steps.append(f"Length = width + {diff}")

    half = re.search(r'half.*?(\d+)', text)
    full = re.search(r'perimeter.*?(\d+)', text)

    if half:
        p = 2 * int(half.group(1))
        steps.append(f"Half perimeter → {p}")
    elif full:
        p = int(full.group(1))
        steps.append(f"Perimeter = {p}")
    else:
        p = None

    if p:
        eq = sp.Eq(2 * (length + width), p)
        sol = sp.solve(eq, x)[0]

        return {
            "type": "rectangle",
            "width": sol,
            "length": length.subs(x, sol),
            "equations": [eq],
            "steps": steps + ["Used: 2(L + W)"]
        }

    return None

# ---------------- ALGEBRA ----------------
def solve_algebra(text):
    eqs = []
    nums = list(map(int, re.findall(r'\d+', text)))

    if "sum" in text and nums:
        eqs.append(sp.Eq(x + y, nums[0]))

    if "difference" in text and nums:
        eqs.append(sp.Eq(x - y, nums[0]))

    if "product" in text and nums:
        eqs.append(sp.Eq(x * y, nums[0]))

    if "times" in text and nums:
        eqs.append(sp.Eq(x, nums[0] * y))

    if "=" in text:
        lhs, rhs = text.split("=")
        eqs.append(sp.Eq(sp.sympify(lhs), sp.sympify(rhs)))

    if eqs:
        sol = sp.solve(eqs, (x, y))
        return {
            "type": "algebra",
            "solution": sol,
            "equations": eqs,
            "steps": ["Formed equations and solved"]
        }

    return None

# ---------------- SPEED ----------------
def solve_speed(text):
    nums = list(map(int, re.findall(r'\d+', text)))

    if "distance" in text and "time" in text and len(nums) >= 2:
        return {"type":"speed","speed":nums[0]/nums[1],"steps":["Speed = D/T"]}

    if "speed" in text and "time" in text and len(nums) >= 2:
        return {"type":"speed","distance":nums[0]*nums[1],"steps":["D = S×T"]}

    if "distance" in text and "speed" in text and len(nums) >= 2:
        return {"type":"speed","time":nums[0]/nums[1],"steps":["T = D/S"]}

    return None

# ---------------- PROFIT ----------------
def solve_profit(text):
    nums = list(map(int, re.findall(r'\d+', text)))

    if "cost" in text and "selling" in text and len(nums) >= 2:
        return {
            "type": "profit",
            "profit": nums[1] - nums[0],
            "steps": ["Profit = SP - CP"]
        }

    return None

# ---------------- AGE ----------------
def solve_age(text):
    if "age" not in text:
        return None

    return {
        "type": "age",
        "steps": [
            "Let age = x",
            "Form equations using relations (expand logic for full solving)"
        ]
    }

# ---------------- SMART ENGINE ----------------
def smart_engine(text):
    text = clean(text)

    for solver in [
        solve_rectangle,
        solve_speed,
        solve_profit,
        solve_age,
        solve_algebra
    ]:
        result = solver(text)
        if result:
            return result

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
st.sidebar.title("🚀 MaySolver ENGINE MAX")
page = st.sidebar.radio("Menu", ["Solver", "Graph", "History"])

if page == "Solver":
    st.title("🧠 MaySolver ENGINE MAX")

    user_input = st.text_area("Enter problem:")

    if st.button("Solve"):
        result = smart_engine(user_input)

        if result:
            st.success("✅ Solved")

            if "equations" in result:
                for eq in result["equations"]:
                    st.latex(sp.latex(eq))

            for step in result["steps"]:
                st.write("•", step)

            st.subheader("Answer")
            for k, v in result.items():
                if k not in ["type","steps","equations"]:
                    st.write(f"{k} = {v}")

            st.session_state["eqs"] = result.get("equations", [])

            st.session_state.history.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "input": user_input,
                "output": str(result)
            })

        else:
            st.error("❌ Could not understand")

elif page == "Graph":
    st.title("📊 Graph")
    if "eqs" in st.session_state:
        st.plotly_chart(plot_graph(st.session_state["eqs"]))
    else:
        st.info("Solve something first")

elif page == "History":
    st.title("🧾 History")
    for item in reversed(st.session_state.history):
        st.write(item)

st.markdown("<center>🚀 MaySolver ENGINE MAX (No API)</center>", unsafe_allow_html=True)
