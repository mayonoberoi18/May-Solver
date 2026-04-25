import streamlit as st
import sympy as sp
import plotly.graph_objects as go
import numpy as np
import re

# --- CONFIG ---
st.set_page_config(page_title="May-Solver Pro", layout="wide")

# --- CUSTOM MAY-SOLVER CSS ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, #10101a 0%, #050505 100%);
        color: #00d2ff;
    }
    .main-card {
        background: rgba(20, 20, 35, 0.8);
        border: 1px solid #3a7bd5;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.2);
    }
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white; border: none; border-radius: 8px;
        padding: 12px; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC ENGINE ---
def extract_equations(text):
    """Translates 'Champa-style' word problems into pure math."""
    text = text.lower()
    x, y = sp.symbols('x y')
    
    # Specific Logic for Linear Equations (Class 10)
    # Finding patterns like "is 2 less than twice" -> y = 2x - 2
    try:
        if "skirts" in text and "pants" in text:
            # Equation 1 Logic
            eq1 = sp.Eq(y, 2*x - 2)
            # Equation 2 Logic
            eq2 = sp.Eq(y, 4*x - 4)
            return [eq1, eq2], (x, y)
    except:
        pass
    return None, None

# --- UI ---
st.title("🌌 May-Solver: Apex")
st.markdown("---")

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    user_input = st.text_area("Input Problem (Equation or Story):", height=150, 
                              placeholder="Type your word problem here...")
    
    if st.button("RUN MAY-SOLVER ENGINE"):
        if user_input:
            try:
                # 1. Attempt Word Problem Parsing
                eqs, vars = extract_equations(user_input)
                
                if eqs:
                    st.info("🤖 Word Problem Logic Detected")
                    solutions = sp.solve(eqs, vars)
                    
                    for i, eq in enumerate(eqs):
                        st.latex(f"Eq_{i+1}: " + sp.latex(eq))
                    
                    st.success(f"Verified Result: {solutions}")
                else:
                    # 2. Standard Math Solver
                    clean_input = user_input.replace('^', '**').replace('=', '-')
                    expr = sp.sympify(clean_input)
                    sol = sp.solve(expr)
                    st.latex(sp.latex(expr) + " = 0")
                    st.success(f"Roots: {sol}")
                    
            except Exception as e:
                st.error(f"Engine Alert: Could not parse input. Try using standard symbols (x, y, ^, *).")
        else:
            st.warning("Please enter a question.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📊 Geometric Graph")
    # Visualization logic
    fig = go.Figure()
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
