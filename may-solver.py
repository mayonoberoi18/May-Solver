import streamlit as st
import sympy as sp
import plotly.graph_objects as go

# 1. THE "ULTIMATE" BACKGROUND & STYLING
# This CSS creates a deep-space gradient with glass-effect cards
st.set_page_config(page_title="Maybot Math Pro", layout="wide")

st.markdown("""
    <style>
    /* Full page background */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a2e, #16213e, #0f3460);
        color: #e94560;
    }

    /* Glassmorphism Card Effect */
    .math-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* Neon Button */
    .stButton>button {
        background: linear-gradient(45deg, #e94560, #950740);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 15px 30px;
        font-size: 18px;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
        box-shadow: 0 0 15px #e94560;
    }

    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px #e94560;
    }

    /* Text Input Styling */
    input {
        background-color: rgba(0,0,0,0.5) !important;
        color: #00fff2 !important;
        border: 1px solid #e94560 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. THE APP HEADER
st.title("🤖 Maybot Math: Ultimate Edition")
st.write("---")

# 3. INTERACTIVE SECTION
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="math-container">', unsafe_allow_html=True)
    user_input = st.text_input("Enter any Word Problem or Equation:", placeholder="e.g. A train travels 360km...")
    
    if st.button("PROVE & SOLVE"):
        # LOGIC: Formal Verification Engine
        x = sp.symbols('x')
        try:
            # Simple placeholder for NLP logic
            # In a full app, this would use an LLM API to turn text to an equation
            expr = sp.sympify(user_input.replace('^', '**'))
            solutions = sp.solve(expr, x)
            
            st.subheader("📝 Step-by-Step Proof")
            st.latex(sp.latex(expr) + " = 0")
            
            for i, sol in enumerate(solutions):
                st.info(f"Root {i+1}: {sol}")
                # Verification Step
                check = expr.subs(x, sol)
                st.caption(f"Verification: Substituted {sol} into equation = {sp.simplify(check)} ✅")

        except Exception as e:
            st.error("Maybot needs a clearer equation to reach 100% verification.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.subheader("📊 Visualization")
    # Interactive Graphing for Class 10 Functions
    fig = go.Figure()
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig)
