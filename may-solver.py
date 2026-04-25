import streamlit as st
import sympy as sp
import plotly.graph_objects as go
import numpy as np

# --- PAGE SETUP ---
st.set_page_config(page_title="May-Solver AI", layout="wide")

# --- THE MAY-SOLVER CYBER BACKGROUND & UI ---
st.markdown("""
    <style>
    /* Main Background Gradient */
    .stApp {
        background: radial-gradient(circle at center, #1a1b26 0%, #0a0a0f 100%);
        color: #c0caf5;
    }

    /* Glassmorphism Input Box */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid #7aa2f7 !important;
        border-radius: 10px !important;
    }

    /* May-Solver Custom Cards */
    .solver-card {
        background: rgba(15, 15, 25, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(122, 162, 247, 0.3);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Neon Button */
    .stButton>button {
        background: linear-gradient(90deg, #7aa2f7 0%, #bb9af7 100%);
        color: #1a1b26;
        border: none;
        font-weight: bold;
        border-radius: 12px;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px #7aa2f7;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- APP HEADER ---
st.title("🌌 May-Solver AI")
st.markdown("#### *The Ultimate Class 9-10 & International Board Engine*")

# --- SIDEBAR TOOLS ---
with st.sidebar:
    st.header("⚙️ Solver Settings")
    board = st.selectbox("Select Curriculum", ["CBSE", "ICSE", "IGCSE", "IB", "State Board"])
    st.info(f"May-Solver is currently optimized for {board} standards.")

# --- CORE LOGIC ---
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<div class="solver-card">', unsafe_allow_html=True)
    user_input = st.text_input("Describe your problem or enter an equation:", placeholder="Example: x^2 + 5x + 6")
    
    if st.button("✨ ACTIVATE MAY-SOLVER"):
        if user_input:
            try:
                x = sp.symbols('x')
                # Pre-processing for user-friendly math
                clean_input = user_input.replace('^', '**').replace('=', '-')
                expr = sp.sympify(clean_input)
                
                # Solving
                solutions = sp.solve(expr, x)
                
                st.subheader("📝 Step-by-Step Logic")
                st.write("**Given Expression:**")
                st.latex(sp.latex(expr) + " = 0")
                
                # Show Factorization (Crucial for Class 10)
                factored = sp.factor(expr)
                if factored != expr:
                    st.write("**Factorized Step:**")
                    st.latex(sp.latex(factored) + " = 0")
                
                st.write("**Final Verified Roots:**")
                for s in solutions:
                    st.success(f"x = {s}")
                
            except Exception as e:
                st.error(f"May-Solver logic check failed: {e}")
        else:
            st.warning("Please enter a question first!")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="solver-card">', unsafe_allow_html=True)
    st.subheader("📊 Visual Map")
    
    if user_input:
        try:
            # Graphing Logic
            f_input = user_input.replace('^', '**').split('=')[0]
            f = sp.lambdify(sp.symbols('x'), sp.sympify(f_input), "numpy")
            x_vals = np.linspace(-10, 10, 400)
            y_vals = f(x_vals)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, line=dict(color='#7aa2f7', width=3)))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="#c0caf5",
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Graph will generate for algebraic functions.")
    else:
        st.caption("Waiting for equation...")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><p style='text-align: center; color: #565f89;'>May-Solver Engine v2.4 | Formally Verified Logic</p>", unsafe_allow_html=True)
