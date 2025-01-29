
"""
this is a simple login functionality using NEON and Streamlit.
"""

import os
import uuid
import hashlib
import pandas as pd
import streamlit as st
import neon

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

    if username in users_db['username'].values:
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
                neon.create_table(CONN, f"{username}_Mapper", {
                                        "guid": "UUID PRIMARY KEY",  # Unique identifier
                                        "name": "VARCHAR(1000)",
                                        "data": "VARCHAR(1000000)"
                                    })
                neon.create_table(CONN, f"{username}_Quelle", {
                                    "guid": "UUID PRIMARY KEY",  # Unique identifier
                                    "API": "VARCHAR(255) NOT NULL",
                                    "file_name": "VARCHAR(255) NOT NULL",
                                    "entity_name": "VARCHAR(255) NOT NULL",
                                    "entity_attributes": "JSONB NOT NULL",
                                    "added_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"  # Auto-timestamp
                                    })
                neon.create_table(CONN, f"{username}_Ziel", {
                                    "guid": "UUID PRIMARY KEY",  # Unique identifier
                                    "API": "VARCHAR(255) NOT NULL",
                                    "file_name": "VARCHAR(255) NOT NULL",
                                    "entity_name": "VARCHAR(255) NOT NULL",
                                    "entity_attributes": "JSONB NOT NULL",
                                    "added_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"  # Auto-timestamp
                                    })
                neon.create_table(CONN, f"{username}_FDM", {
                                    "guid": "UUID PRIMARY KEY",  # Unique identifier
                                    "entity_name": "VARCHAR(255) NOT NULL",  #
                                    "attributes": "JSONB NOT NULL",
                                    "added_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"  # Auto-timestamp
                                    })
                neon.write_to_db(CONN, f"{username}_FDM", {
                                    "guid": str(uuid.uuid4()),  # Unique identifier
                                    "entity_name": "1",
                                    "entity_attributes": [],
                                    })
                neon.write_to_db(CONN, "log", {
                    'guid': str(uuid.uuid4()),
                    'activity_type': "create user",
                    'activity_desc': f"created {username}",
                    'user_name': username,
                    'sst': ""})
                st.success(f"Konto für {email} wurde erfolgreich erstellt!")

            else:
                st.error("Ein Benutzer mit dieser E-Mail-Adresse existiert bereits.")
        else:
            st.warning("Bitte alle Felder ausfüllen.")

def display_forgot_pw():
    """Display the password reset interface."""
    st.subheader("Passwort zurücksetzen")

    email = st.text_input("Bitte geben Sie Ihre E-Mail-Adresse ein, um Ihr Passwort zurückzusetzen.")

    if st.button("Passwort zurücksetzen"):
        users_db = load_users()

        if email in users_db['email'].values:
            st.success("Ein Link zum Zurücksetzen Ihres Passworts wurde an Ihre E-Mail gesendet.")
            st.warning("Funktioniert noch nicht.")
        else:
            st.error("Diese E-Mail-Adresse wurde nicht gefunden.")


# Entry Point
def test_page():
    """Main function to display the interface."""
    option = st.sidebar.selectbox("Navigation", ["Login", "Signup", "Passwort vergessen"])

    if option == "Login":
        display_login()
    elif option == "Signup":
        display_signup()
    elif option == "Passwort vergessen":
        display_forgot_pw()

if __name__ == "__main__":
    test_page()
