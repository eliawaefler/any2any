
"""
this is a simple login functionality using NEON and Streamlit.
user for any2any but could be used for every app like this
"""

import os
import time
import uuid
import hashlib
import pandas as pd
import streamlit as st
from utils import neon
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Constants
CONN = os.environ["NEON_URL_any"]


# Helper Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_salt():
    return hash_password(str(uuid.uuid4()))


# User Management Functions
def load_users():
    neon_users = neon.read_db(CONN, "users")
    users = pd.DataFrame([
        {"guid": u[0], "username": u[1], "email": u[2], "pw_hash": u[3],
         "first_name": u[4], "last_name": u[5], "salt": u[6]}
        for u in neon_users])
    return users


def register_user(username, email, password, first_name, last_name):
    """Register a new user."""
    users_db = load_users()
    st.write(f"username {username}")

    if username in users_db['username'].values:
        st.write("username in db")
        time.sleep(1)
        return False  # Username already exists
    else:
        st.success("username free")
    if email in users_db['email'].values:
        st.write("email in db")
        time.sleep(1)
        return False  # Email already exists
    salt = generate_salt()
    new_user = {
        'guid': str(uuid.uuid4()),
        'username': username,
        'email': email,
        'pw_hash': hash_password(f"{salt}_{password}_{username}"),
        'first_name': first_name,
        'last_name': last_name,
        'salt': salt
    }
    neon.write_to_db(CONN, "users", new_user)
    st.write("successfully updatet user")
    return True


def verify_user(email_or_username, password_given):
    """Verify user credentials."""
    users_db = load_users()
    user = users_db[(users_db['email'] == email_or_username) | (users_db['username'] == email_or_username)]

    if not user.empty:
        user = user.iloc[0]
        expected_hash = hash_password(f"{user['salt']}_{password_given}_{user['username']}")
        if user['pw_hash'] == expected_hash:
            neon.write_to_db(CONN, "log", {
                'guid': str(uuid.uuid4()),
                'activity_type': "login",
                'activity_desc': f"user {email_or_username} logged in",
                'user_name': user['username'],
                'sst': ""})
            return [True, user['username']]

    return [False, ""]


# Streamlit Interface
def display_login():
    """Display the login interface."""

    st.subheader("Login")
    email = st.text_input("Email oder username")
    password = st.text_input("Passwort", type='password')

    if st.button("Login"):
        if email and password:
            authenticated, username = verify_user(email, password)
            if authenticated:
                st.success(f"welcome {username}")
                return username
            else:
                st.warning("Ungültige Email/Passwort Kombination")
        else:
            st.warning("Bitte alle Felder ausfüllen.")


def display_signup():
    """Display the signup interface."""
    st.subheader("Registrieren Sie sich")
    username = st.text_input("Benutzername")
    email = st.text_input("Email")
    password = st.text_input("Passwort", type='password')
    first_name = st.text_input("Vorname")
    last_name = st.text_input("Nachname")

    if st.button("Registrieren"):
        if username and email and password and first_name and last_name:
            if register_user(username, email, password, first_name, last_name):
                return username
            else:
                st.error("Ein Benutzer mit dieser E-Mail-Adresse oder diesem Username existiert bereits.")
        else:
            st.warning("Bitte alle Felder ausfüllen.")


def display_forgot_pw():
    """Display the password reset interface."""
    st.subheader("Passwort zurücksetzen")

    if "email" not in st.session_state:
        st.session_state["email"] = ""
    if "send_time" not in st.session_state:
        st.session_state["send_time"] = time.time()
    st.write(f"send time {st.session_state.send_time % 1000:.2f}")
    if "reset_pw" not in st.session_state:
        st.session_state["reset_pw"] = False
    if "user_record" not in st.session_state:
        st.session_state["user_record"] = False
    st.session_state.email = st.text_input("Bitte geben Sie Ihre E-Mail-Adresse ein, um Ihr Passwort zurückzusetzen.")

    if st.session_state.send_time + 60 <= time.time():
        st.session_state.reset_pw = False
        st.rerun()

    if st.session_state.reset_pw == "send_code":
        send_pw_reset_email(st.session_state.email, st.session_state.code)
        st.success("Ein CODE zum Zurücksetzen Ihres Passworts wurde an Ihre E-Mail gesendet.")
        st.session_state["new_pw"] = False
        st.session_state["code_inp"] = False
        st.text("der CODE läuft in 120 Sekunden ab.")
        st.session_state.code_input = st.text_input("Geben sie hier den CODE ein: ")
        if st.button("check"):
            if st.session_state.send_time + 120 >= time.time() >= st.session_state.send_time + 1:
                st.session_state.send_time = time.time()
                if str(st.session_state.code_input) == str(st.session_state.code):
                    st.session_state.reset_pw = "code_correct"
                    st.rerun()
                else:
                    st.warning("wrong code")
                    time.sleep(1)
                    st.session_state.reset_pw = False
                    st.rerun()
            else:
                st.warning("code expired")
                time.sleep(1)
                st.session_state.reset_pw = False
                st.rerun()

    elif st.session_state.reset_pw == "code_correct":
        st.success("code is correct")
        st.session_state.new_pw = st.text_input("geben Sie ein neues Passwort ein: ", type="password")
        st.session_state["confirm_pw"] = st.text_input(" neues Passwort bestätigen: ", type="password")
        if st.button("change"):
            if st.session_state.send_time + 120 >= time.time() >= st.session_state.send_time + 1:
                if st.session_state.new_pw:
                    if st.session_state.new_pw == st.session_state.confirm_pw:
                        st.session_state.reset_pw = "change"
                        st.rerun()
                    else:
                        st.warning("pws dont match")
                else:
                    st.warning("enter new pw")
            else:
                st.warning("time expired")

    elif st.session_state.reset_pw == "change":
        neon.delete_record(CONN, "users", "email", st.session_state.email)
        user = st.session_state.user_record
        if register_user(str(user["username"].values)[2:-2], str(user["email"].values)[2:-2], st.session_state.new_pw,
                         str(user["first_name"].values)[2:-2], str(user["last_name"].values)[2:-2]):
            st.success("pw changed")
            time.sleep(3)
            st.session_state.reset_pw = False
            return st.session_state.email
        else:
            st.error("smt went wrong")
            st.rerun()
    else:
        if st.button("Passwort zurücksetzen"):
            users_db = load_users()
            if st.session_state.email in users_db['email'].values:
                st.session_state.send_time = time.time()
                st.session_state.user_record = users_db[users_db['email'] == st.session_state.email]
                st.session_state["code"] = generate_salt()[:9]
                st.success("found email")
                st.session_state.reset_pw = "send_code"
                st.rerun()
            else:
                st.error("Diese E-Mail-Adresse wurde nicht gefunden.")


# Email to reset PW
def send_pw_reset_email(address, code):
    subj = "RESET YOUR any2any PASSWORD"
    text = (f"""
    Hello,

    here is your password reset code:
            
            {code} 
            
    kind regards,
    your any2any Team""")
    send_email(address, subj, text)
    return True


def send_email(receiver_email, subject, body):

    # Email credentials
    sender_email = "noreply.any2any@gmail.com"
    password =  os.environ["any2any_admin"]

    # Create email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Send email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")


# Entry Point for TESTING
def test_page():
    option = st.sidebar.selectbox("Navigation", ["Login", "Signup", "Passwort vergessen"])
    if option == "Login":
        display_login()
    elif option == "Signup":
        display_signup()
    elif option == "Passwort vergessen":
        if display_forgot_pw():
            st.rerun()


if __name__ == "__main__":
    test_page()
    #send_email("@gmail.com", "test", "hello")
