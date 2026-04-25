import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
import re
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MaySolver Stable", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    color: white;
}
.box {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SYMBOLS ----------------
x, y = sp.symbols('x y')

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- SAFE PARSER ----------------
def safe_sympy(expr):
    try:
        return sp.sympify(expr)
    except:
        return None

# ---------------- WORD PROBLEM HANDLER ----------------
def solve_word_problem(text):
    text = text.lower()

    # convert words → numbers
    words = {
        "one":1,"two":2,"three":3,"four":4,"five":5,
        "six":6,"seven":7,"eight":8,"nine":9,"ten":10
    }
    for w,n in words.items():
        text = text.replace(w, str(n))

    nums = list(map(int, re.findall(r'\d+', text)))

    try:
        # difference + multiple pattern
        if "difference" in text and "times" in text and len(nums) >= 2:
            eq1 = sp.Eq(x - y, nums[0])
            eq2 = sp.Eq(x, nums[1]*y)
            sol = sp.solve((eq1, eq2), (x,y))
            return sol, [eq1, eq2], "Word Problem"

        # sum + multiple
        if "sum" in text and "times" in text and len(nums) >= 2:
            eq1 = sp.Eq(x + y, nums[0])
            eq2 = sp.Eq(x, nums[1]*y)
            sol = sp.solve((eq1, eq2), (x,y))
            return sol, [eq1, eq2], "Word Problem"

    except:
        pass

    return None, None, None

# ---------------- MAIN SOLVER ----------------
def solve_math(user_input):
    text = user_input.strip()

    # 1. Try word problem
    sol, eqs, cat = solve_word_problem(text)
    if sol:
        return sol, eqs, cat

    # 2. Try equation
    if "=" in text:
        try:
            lhs, rhs = text.split("=")
            lhs_expr = safe_sympy(lhs)
            rhs_expr = safe_sympy(rhs)

            if lhs_expr is not None and rhs_expr is not None:
                eq = sp.Eq(lhs_expr, rhs_expr)
                sol = sp.solve(eq)
                return sol, [eq], "Equation"
        except:
            pass

    # 3. Try expression
    expr = safe_sympy(text)
    if expr is not None:
        try:
            sol = sp.solve(expr)
            return sol, [expr], "Expression"
        except:
            pass

    return None, None, "Could not understand input"

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
page = st.sidebar.radio("Menu", ["Solver", "Graph", "History", "About"])

# -------- SOLVER --------
if page == "Solver":
    st.title("🧠 Smart Math Solver")

    user_input = st.text_area("Enter problem:")

    if st.button("Solve"):
        if user_input:
            with st.spinner("Solving..."):

                sol, eqs, cat = solve_math(user_input)

                if eqs:
                    st.success(f"Detected: {cat}")

                    st.subheader("🧾 Equations")
                    for eq in eqs:
                        st.latex(sp.latex(eq))

                    st.subheader("✅ Answer")
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

# -------- ABOUT --------
elif page == "About":
    st.title("About")
    st.write("Stable Math Solver (No API, No Errors)")

st.markdown("<center>🚀 MaySolver Stable Version</center>", unsafe_allow_html=True)
