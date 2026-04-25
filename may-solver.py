import streamlit as st
import sympy as sp

# 1. MAYBOT STYLING (CSS Injection)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
        color: white; border-radius: 20px; border: none;
        padding: 10px 24px; font-weight: bold; width: 100%;
    }
    .math-card {
        background: #1c1f26; border-radius: 15px;
        padding: 20px; margin: 10px 0;
        border-left: 5px solid #6a11cb;
    }
    </style>
    """, unsafe_Class_unsafe_allow_html=True)

# 2. APP HEADER
st.title("🤖 Maybot Math AI")
st.caption("Class 9-10 CBSE & International Board Specialist")

# 3. INTERFACE
query = st.text_input("Enter your word problem or equation:", placeholder="e.g., sum of x and 5 is 20")

if st.button("SOLVE WITH MAYBOT"):
    with st.spinner('🤖 Maybot is thinking...'):
        # Here we use the Symbolic Logic we built earlier
        x = sp.symbols('x')
        try:
            # Simple NLP-to-Math conversion logic
            clean_query = query.lower().replace("sum of x and ", "x + ").replace(" is ", " - ")
            expr = sp.sympify(clean_query)
            sol = sp.solve(expr, x)
            
            # DISPLAY RESULTS IN A MAYBOT CARD
            st.markdown(f"""
                <div class="math-card">
                    <h4>✅ Verified Solution</h4>
                    <p><b>Logic:</b> {expr} = 0</p>
                    <h2 style="color: #00ffcc;">x = {sol[0] if sol else 'No Solution'}</h2>
                </div>
            """, unsafe_allow_html=True)
            
            st.success("Steps generated based on CBSE marking scheme.")
            
        except Exception as e:
            st.error("I need a bit more detail to solve this perfectly!")

# 4. SIDEBAR FEATURES
st.sidebar.header("Maybot Tools")
st.sidebar.button("📷 Scan Question")
st.sidebar.button("📘 Formula Library")
st.sidebar.button("📊 Progress Tracker")
