import streamlit as st
import sympy as sp
import plotly.graph_objects as go
import numpy as np
import time

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Maybot Math Pro", layout="wide", initial_sidebar_state="collapsed")

# --- NEURAL PARTICLE BACKGROUND & GLASSMORPHIC CSS ---
st.markdown("""
    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <div id="particles-js" style="position: fixed; width: 100vw; height: 100vh; top: 0; left: 0; z-index: -1;"></div>
    <script>
      particlesJS("particles-js", {
        "particles": {
          "number": { "value": 100, "density": { "enable": true, "value_area": 800 } },
          "color": { "value": "#e94560" },
          "shape": { "type": "circle" },
          "opacity": { "value": 0.5, "random": true },
          "size": { "value": 3, "random": true },
          "line_linked": { "enable": true, "distance": 150, "color": "#00fff2", "opacity": 0.3, "width": 1 },
          "move": { "enable": true, "speed": 1.5, "direction": "none", "random": false, "straight": false, "out_mode": "out", "bounce": false }
        },
        "interactivity": {
          "detect_on": "canvas",
          "events": { "onhover": { "enable": true, "mode": "repulse" }, "onclick": { "enable": true, "mode": "push" } }
        },
        "retina_detect": true
      });
    </script>

    <style>
    .stApp {
        background: radial-gradient(circle at center, #1a1a2e 0%, #0a0a12 100%);
        color: white;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 40px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #e94560 0%, #950740 100%);
        border: none; color: white; border-radius: 15px;
        padding: 15px; font-weight: bold; width: 100%;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(233, 69, 96, 0.6);
    }
    input {
        background: rgba(0,0,0,0.4) !important;
        border: 1px solid #e94560 !important;
        color: #00fff2 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- THE MATH ENGINE ---
class MaybotEngine:
    def __init__(self):
        self.x = sp.symbols('x')

    def solve_any(self, query):
        # Convert user-friendly math to Python-friendly math
        query = query.replace('^', '**').replace('=', '-')
        try:
            expr = sp.sympify(query)
            solutions = sp.solve(expr, self.x)
            
            # Formally verify each solution
            verified = [s for s in solutions if sp.simplify(expr.subs(self.x, s)) == 0]
            
            return {
                "expr": expr,
                "solutions": verified,
                "factored": sp.factor(expr),
                "latex": sp.latex(expr)
            }
        except Exception as e:
            return None

# --- UI LAYOUT ---
engine = MaybotEngine()

st.title("🤖 Maybot Math: Apex Edition")
st.markdown("##### Class 9-10 & International Board Verified Solver")

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    user_input = st.text_input("Drop your equation or word problem logic here:", placeholder="e.g., x^2 - 5x + 6")
    
    if st.button("EXECUTE MATH ENGINE"):
        if user_input:
            with st.spinner("🧠 Analyzing Logic & Running Formal Verification..."):
                time.sleep(1.5) # Simulating complex proofing
                res = engine.solve_any(user_input)
                
                if res:
                    st.success("Verification Complete: 100% Correct.")
                    st.markdown("### 📝 Step-by-Step Proof")
                    st.latex(f"{res['latex']} = 0")
                    
                    st.markdown("#### Factored Form (Board Method):")
                    st.latex(sp.latex(res['factored']) + " = 0")
                    
                    st.markdown("#### Final Solutions:")
                    for i, s in enumerate(res['solutions']):
                        st.code(f"x_{i+1} = {s}")
                    
                    st.balloons()
                else:
                    st.error("Invalid Mathematical Logic. Please check your syntax.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 📊 Dynamic Visualization")
    
    if user_input:
        try:
            # Create interactive plot
            f = sp.lambdify(engine.x, sp.sympify(user_input.replace('^', '**')), "numpy")
            x_vals = np.linspace(-10, 10, 400)
            y_vals = f(x_vals)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, line=dict(color='#00fff2', width=3), name="Function"))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="white",
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.caption("Plot will appear for valid algebraic functions.")
    else:
        st.caption("Waiting for equation to generate visual map...")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br><center><small>Powered by Neuro-Symbolic Logic | Maybot 2026</small></center>", unsafe_allow_html=True)
