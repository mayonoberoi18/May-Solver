import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MaySolver AI", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    color: white;
}
.block {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SYMBOLS ----------------
x, y, z = sp.symbols('x y z')

# ---------------- SESSION ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- AI TRANSLATOR ----------------
def ai_to_math(problem):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        prompt = f"""
        Convert the following word problem into mathematical equations using variables x, y, z.

        Only return equations. No explanation.

        Problem:
        {problem}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            timeout=10
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return None

# ---------------- PARSER ----------------
def parse_equations(text):
    equations = []
    lines = text.split("\n")

    for line in lines:
        if "=" in line:
            try:
                lhs, rhs = line.split("=")
                eq = sp.Eq(sp.sympify(lhs.strip()), sp.sympify(rhs.strip()))
                equations.append(eq)
            except:
                continue

    return equations

# ---------------- SOLVER ----------------
def solve_problem(user_input):
    # Try AI first
    ai_output = ai_to_math(user_input)

    if ai_output:
        eqs = parse_equations(ai_output)
        if eqs:
            try:
                sol = sp.solve(eqs)
                return sol, eqs, "AI Word Problem", ai_output
            except:
                pass

    # Fallback to direct math
    try:
        if "=" in user_input:
            lhs, rhs = user_input.split("=")
            eq = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
            sol = sp.solve(eq)
            return sol, [eq], "Equation", None
        else:
            expr = sp.sympify(user_input)
            sol = sp.solve(expr)
            return sol, [expr], "Expression", None
    except Exception as e:
        return None, None, str(e), None

# ---------------- GRAPH ----------------
def plot_graph(eqs):
    fig = go.Figure()
    x_vals = np.linspace(-10, 10, 300)

    for eq in eqs:
        try:
            y_expr = sp.solve(eq, y)
            if y_expr:
                f = sp.lambdify(x, y_expr[0], "numpy")
                y_vals = f(x_vals)

                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode='lines',
                    name=str(eq)
                ))
        except:
            continue

    fig.update_layout(template="plotly_dark")
    return fig

# ---------------- UI ----------------
st.sidebar.title("🚀 MaySolver AI")
page = st.sidebar.radio("Navigate", ["Solver", "Graph", "History", "About"])

# -------- SOLVER --------
if page == "Solver":
    st.title("🧠 AI Math Solver")

    user_input = st.text_area("Enter any math problem:")

    if st.button("Solve"):
        if user_input:
            with st.spinner("Thinking..."):

                sol, eqs, cat, ai_text = solve_problem(user_input)

                if eqs:
                    st.success(f"Detected: {cat}")

                    if ai_text:
                        st.subheader("🤖 AI Converted Problem")
                        st.code(ai_text)

                    st.subheader("🧾 Equations")
                    for eq in eqs:
                        st.latex(sp.latex(eq))

                    st.subheader("✅ Answer")
                    st.write(sol)

                    st.session_state["eqs"] = eqs

                    # Save history
                    st.session_state.history.append({
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "input": user_input,
                        "output": str(sol)
                    })

                else:
                    st.error(cat)

# -------- GRAPH --------
elif page == "Graph":
    st.title("📊 Graph Visualizer")

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
    st.title("🔥 About")
    st.write("""
    MaySolver AI:
    - Understands word problems
    - Solves equations
    - Graphs results
    - Uses AI + SymPy
    """)

st.markdown("<center>🚀 MaySolver AI | Final Version</center>", unsafe_allow_html=True)
