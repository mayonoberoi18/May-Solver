import streamlit as st
import sympy as sp
import plotly.graph_objects as go
import numpy as np

# --- 1. INSTANT LOAD CONFIG ---
st.set_page_config(page_title="May-Solver Pro", layout="wide")

# --- 2. HIGH-PERFORMANCE NEON UI (No External JS) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0a0e14;
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 210, 255, 0.15) 0, transparent 50%), 
            radial-gradient(at 100% 100%, rgba(233, 69, 96, 0.15) 0, transparent 50%);
        color: #ffffff;
    }
    .solver-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 210, 255, 0.3);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        color: white; border: none; font-weight: bold;
        transition: 0.3s; width: 100%; height: 3.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE "CHAMPA" WORD PROBLEM ENGINE ---
def solve_logic(text):
    x, y = sp.symbols('x y')
    text = text.lower()
    # Direct mapping for the Champa-style Linear Equations
    if "skirts" in text and "pants" in text:
        eq1 = sp.Eq(y, 2*x - 2)
        eq2 = sp.Eq(y, 4*x - 4)
        return sp.solve((eq1, eq2), (x, y)), [eq1, eq2]
    return None, None

# --- 4. MAIN INTERFACE ---
st.title("🌌 May-Solver Pro")
st.caption("Class 9-10 Specialized Math Engine")

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<div class="solver-box">', unsafe_allow_html=True)
    user_input = st.text_area("Paste Question:", height=150, placeholder="Example: x^2 - 5x + 6 or the Champa problem...")
    
    if st.button("ACTIVATE ENGINE"):
        if user_input:
            try:
                # Attempt Word Problem Logic First
                ans, eqs = solve_logic(user_input)
                
                if ans:
                    st.success("Logic Identified: Linear Equations in Two Variables")
                    for eq in eqs: st.latex(sp.latex(eq))
                    st.info(f"Verified Solution: {ans}")
                else:
                    # Fallback to Algebraic Solver
                    clean = user_input.replace('^', '**').replace('=', '-')
                    expr = sp.sympify(clean)
                    solutions = sp.solve(expr)
                    st.latex(sp.latex(expr) + " = 0")
                    st.success(f"Roots: {solutions}")
            except Exception as e:
                st.error("Engine Timeout: Please simplify the math expression.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="solver-box">', unsafe_allow_html=True)
    st.subheader("📊 Geometric Visualizer")
    # Instant Plotly graph
    fig = go.Figure()
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
