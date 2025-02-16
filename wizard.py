
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
import pyautogui


def take_region_screenshot(x, y, width, height, save_path="screenshot.png"):
    """
    Takes a screenshot of a specific region.

    :param x: Top-left x-coordinate
    :param y: Top-left y-coordinate
    :param width: Width of the screenshot
    :param height: Height of the screenshot
    :param save_path: File path to save the screenshot
    """
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    screenshot.save(save_path)
    print(f"Screenshot saved at {save_path}")


def take_full_screenshot(save_path="screenshot.png"):
    """
    Takes a screenshot of the full screen
    :param save_path: File path to save the screenshot
    """
    screenshot = pyautogui.screenshot()
    screenshot.save(save_path)
    print(f"Screenshot saved at {save_path}")


def construct_arrow(sq_pos, sq_say):

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
        < div style = "
            position: absolute;
            top: {x}px;
            left: {y}px;
            width: {z}px;
            height: {z}px;
            background - color: rgba(255, 0, 0, {o});
            margin: 0;
            transform: rotate(45deg);
            transform - origin: center;
        </div>
        <div style="
            position:absolute;
            top:{x}px;
            left:{y}px;">{sq_say}</div>
        """


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


def wizard_step(my_step, my_goal, old_square, img):
    screen = my_openai.img_to_text(img_base64=my_openai.image_to_base64(f"data/wizard_screenshots/{img}.png"))

    answer = gpt4_new(f"""you are an ai helper on a user interface.
    
    // MOVING:
    you can move around the screen and what you cover will be displayed as a red square.
    the square is defined using a python list with three ints. 
    the first int represents the pixel values of the y coordinate of the 
    bottom left corner, the second number is the x coordinate and the third number is the size of the square in pixels.
    the Square is currently at: <square_position>{old_square}</square_position>. return a list like this to move the square. 
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
    
    // STEP_DONE
    if the step specified below ist 100% completed, no further actions as defined above are neeeded,
    include <step_done>TRUE</step_done> in the answer. Else, if further actions are needed,
     include <step_done>FALSE</step_done> in the answer. 
    
    // GOAL: YOUR OVERARCHING GOAL IS TO:
    {my_goal}//
    
    // STEP: TO REACH THIS, YOU SHOULD NOW: 
    {my_step}//
    
    // SCREEN DESCRIPTION, INSIDE THE RED SQUARE:
    {screen}//

    // INSTRUCTION
    give the new square position, what you want to say, if you want to click somewhere, and if the step is done or not.
    //
    """)
    print(answer)
    new_square = basic_utils.extract_lists_from_string(basic_utils.extract_html_content(answer, "square_position"))[0]
    new_say = basic_utils.extract_html_content(answer, "square_say")
    click = basic_utils.extract_html_content(answer, "square_click")
    step_done = basic_utils.extract_html_content(answer, "step_done")
    if len(new_square) == 0:
        new_square = old_square
    if step_done not in ["TRUE", "True", "Yes"]:
        step_done = False
    else:
        step_done = True
    return [new_square, new_say, step_done]


def wizard_get_steps(my_steps, my_goal):
    pass


def wizard_go():
    sq_placeholder = st.empty()
    say_placeholder = st.empty()
    say = "hello im the square"
    goal = "create a mapper table"
    steps = ["move to the 'create mapper' button", "click on the create new mapper button", "select the quelle"]
    n = 0
    square = [500, 500, 800]
    sq_placeholder.markdown(construct_arrow(square + ["0.2"], say), unsafe_allow_html=True)
    for step in steps:
        st.write(step)
        done = False
        while not done:
            square, say, done = wizard_step(goal, step, square, n)
            sq_placeholder.empty()
            say_placeholder.empty()
            sq_placeholder.markdown(construct_arrow(square + ["0.2"], say), unsafe_allow_html=True)
            n += 1
            y, x, s = square
            take_full_screenshot(f"data/wizard_screenshots/{n}.png")
            if n >= 10:
                return 0


if __name__ == '__main__':
    innit_st_page()
    st.title("ai controll")
    if st.button("home"):
        if st.button("create new mapper"):
            st.success("ai clicked on the button")
    sst = st.session_state
    st.write("square mover")
    if st.button("wizard go"):
        wizard_go()

