import streamlit as st
from multipage import MultiPage
from pages import simulator, alpha_calculator

# Configure Streamlit page
st.set_page_config(
     page_title="Venture Fund Simulator",
     page_icon="🚀",
     layout="centered",
     initial_sidebar_state="expanded",
     menu_items={
         'Get help': None,
         'Report a bug': None,
         'About': "A simulator of venture funds to help build intuition for VC investing."
     }
 )

# Create an instance of the app
app = MultiPage()

# Add all your applications (pages) here
app.add_page("Simulator", simulator.app)
app.add_page("Alpha Parameter Calculator", alpha_calculator.app)

# The main app
app.run()
