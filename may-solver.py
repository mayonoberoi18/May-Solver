import streamlit as st
import sympy as sp
import plotly.graph_objects as go
import numpy as np
import re

st.set_page_config(page_title="May-Solver GOD MODE", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
}
.glass {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# --- SYMBOLS ---
x, y, z = sp.symbols('x y z')

# --- BRAIN ---
class GodBrain:

    def preprocess(self, text):
        text = text.lower()
        text = text.replace("^", "**")
        text = text.replace("equals", "=")
        text = text.replace("is", "=")
        return text

    def extract_equations(self, text):
        parts = re.split(r',|and', text)
        equations = []

        for part in parts:
            if "=" in part:
                try:
                    lhs, rhs = part.split("=")
                    eq = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
                    equations.append(eq)
                except:
                    continue
        return equations

    def solve(self, text):
        text = self.preprocess(text)

        eqs = self.extract_equations(text)

        # MULTI EQUATION SYSTEM
        if len(eqs) > 1:
            try:
                sol = sp.solve(eqs)
                return sol, eqs, "System of Equations"
            except Exception as e:
                return None, None, str(e)

        # SINGLE EQUATION
        if len(eqs) == 1:
            try:
                sol = sp.solve(eqs[0])
                return sol, eqs, "Single Equation"
            except Exception as e:
                return None, None, str(e)

        # EXPRESSION
        try:
            expr = sp.sympify(text)
            sol = sp.solve(expr)
            return sol, [expr], "Expression"
        except Exception as e:
            return None, None, str(e)

# --- GRAPH ---
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

# --- STEPS ---
def show_steps(eqs):
    st.subheader("🧠 Step Breakdown")
    for eq in eqs:
        st.latex(sp.latex(eq))

# --- UI ---
brain = GodBrain()

st.title("🤖 MAY-SOLVER GOD MODE")
st.markdown("### 🚀 Ultimate AI Math Engine")

col1, col2 = st.columns([3,2])

with col1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)

    user_input = st.text_area("Enter anything math:")

    if st.button("⚡ Solve"):
        if user_input:
            with st.spinner("Thinking like a genius..."):
                sol, eqs, cat = brain.solve(user_input)

                if eqs:
                    st.success(f"Detected: {cat}")

                    show_steps(eqs)

                    st.subheader("✅ Answer")
                    st.write(sol)

                    st.session_state["eqs"] = eqs
                else:
                    st.error(cat)

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)

    st.subheader("📊 Graph")

    if "eqs" in st.session_state:
        fig = plot_graph(st.session_state["eqs"])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Solve something first")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center>🔥 GOD MODE ACTIVATED 🔥</center>", unsafe_allow_html=True)
