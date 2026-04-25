import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
import re
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MaySolver Smart", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SYMBOLS ----------------
x, y = sp.symbols('x y')

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- WORD → NUMBER ----------------
def word_to_number(text):
    words = {
        "one":1,"two":2,"three":3,"four":4,"five":5,
        "six":6,"seven":7,"eight":8,"nine":9,"ten":10
    }
    for w,n in words.items():
        text = re.sub(rf"\b{w}\b", str(n), text)
    return text

# ---------------- SMART PARSER ----------------
def smart_parser(text):
    text = text.lower()
    text = word_to_number(text)

    # Remove noise words
    text = re.sub(r'\b(numbers?|find|them|and)\b', '', text)

    nums = list(map(int, re.findall(r'\d+', text)))

    try:
        # -------- DIFFERENCE --------
        if "difference" in text:
            diff = nums[0]

            if "times" in text:
                multiplier = nums[1]
                eq1 = sp.Eq(x - y, diff)
                eq2 = sp.Eq(x, multiplier * y)
                return [eq1, eq2]

            elif "sum" in text:
                total = nums[1]
                eq1 = sp.Eq(x - y, diff)
                eq2 = sp.Eq(x + y, total)
                return [eq1, eq2]

        # -------- SUM --------
        if "sum" in text:
            total = nums[0]

            if "times" in text:
                multiplier = nums[1]
                eq1 = sp.Eq(x + y, total)
                eq2 = sp.Eq(x, multiplier * y)
                return [eq1, eq2]

        # -------- DIRECT EQUATION --------
        if "=" in text:
            lhs, rhs = text.split("=")
            eq = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
            return [eq]

    except:
        pass

    return None

# ---------------- SOLVER ----------------
def solve_math(user_input):
    eqs = smart_parser(user_input)

    if eqs:
        try:
            sol = sp.solve(eqs, (x, y))
            return sol, eqs, "Smart Word Problem"
        except:
            pass

    # fallback simple
    try:
        if "=" in user_input:
            lhs, rhs = user_input.split("=")
            eq = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
            sol = sp.solve(eq)
            return sol, [eq], "Equation"
    except:
        pass

    return None, None, "Could not understand"

# ---------------- GRAPH ----------------
def plot_graph(eqs):
    fig = go.Figure()
    x_vals = np.linspace(-10, 10, 200)

    for eq in eqs:
        try:
            y_expr = sp.solve(eq, y)
            if y_expr:
                f = sp.lambdify(x, y_expr[0], "numpy")
                y_vals = f(x_vals)

                fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines'))
        except:
            continue

    fig.update_layout(template="plotly_dark")
    return fig

# ---------------- UI ----------------
st.sidebar.title("🚀 MaySolver")
page = st.sidebar.radio("Menu", ["Solver", "Graph", "History"])

# -------- SOLVER --------
if page == "Solver":
    st.title("🧠 Smart Math Solver")

    user_input = st.text_area("Enter problem:")

    if st.button("Solve"):
        if user_input:
            sol, eqs, cat = solve_math(user_input)

            if eqs:
                st.success(f"Detected: {cat}")

                st.subheader("🧾 Equations")
                for eq in eqs:
                    st.latex(sp.latex(eq))

                st.subheader("✅ Answer")

                # Fix JSON issue
                if isinstance(sol, dict):
                    sol_clean = {str(k): v for k, v in sol.items()}
                    st.write(sol_clean)
                else:
                    st.write(sol)

                st.session_state["eqs"] = eqs

                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "input": user_input,
                    "output": str(sol)
                })

            else:
                st.error(cat)

# -------- GRAPH --------
elif page == "Graph":
    st.title("📊 Graph")

    if "eqs" in st.session_state:
        fig = plot_graph(st.session_state["eqs"])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Solve something first")

# -------- HISTORY --------
elif page == "History":
    st.title("🧾 History")

    if st.session_state.history:
        for item in reversed(st.session_state.history):
            st.markdown(f"""
            **{item['time']}**  
            ➤ {item['input']}  
            ✅ {item['output']}
            """)
    else:
        st.info("No history yet")

st.markdown("<center>🚀 MaySolver Smart Parser Edition</center>", unsafe_allow_html=True)
