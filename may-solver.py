import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
import re
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MaySolver Pro", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    color: white;
}
.glass {
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

# ---------------- BRAIN ----------------
class MathBrain:

    def preprocess(self, text):
        text = text.lower()
        text = text.replace("^", "**")
        text = text.replace("equals", "=")
        text = text.replace("is", "=")
        return text

    def parse_equations(self, text):
        parts = re.split(r',|and', text)
        eqs = []

        for part in parts:
            if "=" in part:
                try:
                    lhs, rhs = part.split("=")
                    eq = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
                    eqs.append(eq)
                except:
                    pass
        return eqs

    def solve(self, text):
        text = self.preprocess(text)

        eqs = self.parse_equations(text)

        # SYSTEM
        if len(eqs) > 1:
            try:
                sol = sp.solve(eqs)
                return sol, eqs, "System"
            except Exception as e:
                return None, None, str(e)

        # SINGLE
        if len(eqs) == 1:
            try:
                sol = sp.solve(eqs[0])
                return sol, eqs, "Equation"
            except Exception as e:
                return None, None, str(e)

        # EXPRESSION
        try:
            expr = sp.sympify(text)
            sol = sp.solve(expr)
            return sol, [expr], "Expression"
        except Exception as e:
            return None, None, str(e)

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

# ---------------- AI (OPTIONAL) ----------------
def ask_ai(question):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Explain math step by step clearly."},
                {"role": "user", "content": question}
            ],
            timeout=10
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"

# ---------------- UI ----------------
brain = MathBrain()

st.sidebar.title("🚀 MaySolver Pro")
page = st.sidebar.radio("Navigate", ["Solver", "Graph", "AI Tutor", "History", "About"])

# -------- SOLVER --------
if page == "Solver":
    st.title("🧠 Smart Solver")

    user_input = st.text_area("Enter math problem:")

    if st.button("Solve"):
        if user_input:
            with st.spinner("Solving..."):
                sol, eqs, cat = brain.solve(user_input)

                if eqs:
                    st.success(f"Detected: {cat}")

                    st.subheader("🧾 Steps")
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

# -------- AI --------
elif page == "AI Tutor":
    st.title("🤖 AI Tutor")

    q = st.text_area("Ask anything")

    if st.button("Get Explanation"):
        if q:
            with st.spinner("Thinking..."):
                st.write(ask_ai(q))

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
    MaySolver Pro:
    - Smart Math Solver
    - Graph Visualizer
    - AI Tutor
    - Built with Streamlit
    """)

st.markdown("<center>🚀 MaySolver Pro | 2026 Edition</center>", unsafe_allow_html=True)
