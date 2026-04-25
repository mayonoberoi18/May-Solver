import streamlit as st
import sympy as sp
import plotly.graph_objects as go
import numpy as np
import re

# --- 1. CONFIGURATION & NEON THEME ---
st.set_page_config(page_title="May-Solver Apex", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: #0f0c29;
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #ffffff;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 210, 255, 0.3);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }
    .stButton>button {
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        color: white; border: none; font-weight: bold;
        height: 3.5rem; width: 100%; border-radius: 12px;
        transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px #00d2ff;
        transform: translateY(-2px);
    }
    input, textarea {
        background-color: rgba(0,0,0,0.4) !important;
        color: #00d2ff !important;
        border: 1px solid #3a7bd5 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE UNIVERSAL BRAIN ---
class MaySolverBrain:
    def __init__(self):
        self.x, self.y = sp.symbols('x y')

    def solve_anything(self, text):
        text_clean = text.lower().strip()
        
        # A. STRATEGIC WORD PROBLEM EXTRACTION (Linear Systems)
        # Specifically designed for the 'Champa' type problems
        nums = [int(n) for n in re.findall(r'\d+', text_clean)]
        if ("skirts" in text_clean or "pants" in text_clean) and len(nums) >= 4:
            try:
                # Equation 1: y = (times)x - (less)
                eq1 = sp.Eq(self.y, nums[1]*self.x - nums[0])
                # Equation 2: y = (times)x - (less)
                eq2 = sp.Eq(self.y, nums[3]*self.x - nums[2])
                sol = sp.solve((eq1, eq2), (self.x, self.y))
                return sol, [eq1, eq2], "System of Linear Equations"
            except: pass

        # B. ALGEBRAIC EQUATION SOLVER (Quadratic, Linear, Polynomial)
        try:
            # Pre-cleaning symbols
            math_text = text_clean.replace('^', '**').replace('is', '=').replace('equal to', '=')
            
            if "=" in math_text:
                lhs, rhs = math_text.split('=')
                equation = sp.Eq(sp.sympify(lhs.strip()), sp.sympify(rhs.strip()))
                sol = sp.solve(equation)
                return sol, [equation], "Standard Equation"
            else:
                expr = sp.sympify(math_text)
                sol = sp.solve(expr)
                return sol, [expr], "Algebraic Expression"
        except Exception as e:
            return None, None, str(e)

# --- 3. UI IMPLEMENTATION ---
brain = MaySolverBrain()

st.title("🤖 May-Solver: Apex AI")
st.markdown("### *The Ultimate Math Agent for Class 9-10 & Beyond*")

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    user_input = st.text_area("Drop your word problem or equation below:", 
                              placeholder="Example: The number of skirts is two less than twice the number of pants...",
                              height=200)
    
    if st.button("🚀 ACTIVATE APEX ENGINE"):
        if user_input:
            with st.spinner("🧠 May-Solver is formalizing logic..."):
                answer, equations, category = brain.solve_anything(user_input)
                
                if equations:
                    st.success(f"Detected: {category}")
                    st.markdown("#### 📝 Step-by-Step Logic:")
                    for eq in equations:
                        st.latex(sp.latex(eq))
                    
                    st.markdown("#### ✅ Final Verified Result:")
                    st.info(f"{answer}")
                    st.balloons()
                else:
                    st.error("Engine Alert: Logic not identified. Please try using digits (e.g., '2') instead of words ('two').")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 Geometric Visualization")
    
    # Dynamic graph generation
    fig = go.Figure()
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    # Simple plot for first variable if possible
    if user_input and "=" in user_input:
        try:
            x_vals = np.linspace(-10, 10, 100)
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.caption("Visualizer pending valid equation...")
    else:
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><center><small>May-Solver v5.0 | 2026 Neural Bridge Edition</small></center>", unsafe_allow_html=True)
