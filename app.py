import streamlit as st
from multipage import MultiPage
from pages import simulator, growth_rates

# Configure Streamlit page
st.set_page_config(
     page_title="Venture Fund Simulator",
     page_icon="🚀",
     layout="centered",
     initial_sidebar_state="expanded",
     menu_items={
         'Get help': None,
         'Report a bug': 'https://github.com/wdesilvestro/vc-simulator/issues',
         'About': "A venture capital simulator to help build intuition for how VC investing works."
     }
 )

# Create an instance of the app
app = MultiPage()

# Add all your applications (pages) here
app.add_page("Simulator", simulator.app)
app.add_page("Growth Rates Calculator", growth_rates.app)

# The main app
app.run()
