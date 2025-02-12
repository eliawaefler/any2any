
"""
WORK IN PROGRESS
GPT4 powered AI helper to create
"""

import time

from utils import neon
from utils import  basic_utils
import streamlit as st
from utils import my_openai

from anwendung import *
from utils.my_openai import gpt4_new

def construct_square(sq_pos, sq_say):

    x, y, z, o = sq_pos
    return f"""
        <div style="
            position:absolute; 
            top: {x}px; 
            left:{y}px; 
            width:{z}px; 
            height:{z}px; 
            background-color:rgba(255, 0, 0, {o}); 
            margin:0;">
        </div>
        <div style="
            position:absolute;
            top:{x}px;
            left:{y}px;">{sq_say}</div>
        """


square = [500, 500, 100]
sst = st.session_state
innit_st_page()
st.write("square mover")
sq_placeholder = st.empty()
say_placeholder = st.empty()
say = "hello im the square"
for n in range(10):

    di_sq = square + ["0.2"]

    sq_placeholder.empty()
    say_placeholder.empty()
    sq_placeholder.markdown(construct_square(di_sq, say), unsafe_allow_html=True)
    st.title("ai controll")
    answer = gpt4_new(f"""you are an ai helper on a user interface.
    
    // MOVING:
    you can move around the screen and what you cover will be displayed as a red square.
    the square is defined using a python list with three ints. 
    the first int represents the pixel values of the y coordinate of the 
    bottom left corner, the second number is the x coordinate and the third number is the size of the square in pixels.
    the Square is currently at: <square_position>{square}</square_position>. return a list like this to move the square. 
    place the list inside a <square_position> html tag. //
    
    // SPEAKING:
    next to the square (or inside it) a speech bubble will be displayed. any text you want to tell the user, 
    you can send in the format: <square_say>YOUR TEXT</square_say> so squeeze anything you want to tell him
    between the <square_say> html tags. //
    
    // CLICKING:
    you can click on any element on the page. 
    the click instruction takes an x and y coordinate (which must be inside of the red square.) 
    and one of the following clicking modes: 'left_one', 'left_double', 'right_one', 'right_double'. 
    format the clicking instruction like this: <square_click>[x, y, 'left_one']</square_click> //
    
    // CUSTOM INSTRUCTION:
    move the square slowly towards top right of the page.
    //
    """)
    square = basic_utils.extract_lists_from_string(basic_utils.extract_html_content(answer, "square_position"))[0]
    say = basic_utils.extract_html_content(answer, "square_say")

