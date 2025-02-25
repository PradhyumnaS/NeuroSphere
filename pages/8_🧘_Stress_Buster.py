import streamlit as st

st.title("🧘 Stress Burster")
    
st.markdown("""
<style>

.spline-container {
    border-radius: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    overflow: hidden;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
### Take a Moment to Unwind 
Interact with our BlueBall and let your stress melt away.
""")

st.markdown("""
<div class="spline-container">
<iframe 
    src='https://my.spline.design/aitherapist-e7816283ccca0cc7f2e74c543a304ec1/' 
    frameborder='0' 
    width='100%' 
    height='500px'>
</iframe>
</div>
""", unsafe_allow_html=True)

st.subheader("Quick Stress Relief Tips")
tips = [
    "Take deep, slow breaths",
    "Practice mindfulness",
    "Stretch or do light exercise",
    "Listen to calming music"
]

for tip in tips:
    st.markdown(f"• {tip}")