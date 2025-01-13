import streamlit as st
import pandas as pd
import hashlib
import json

"""
// TODO: salt for PW
"""

# Pfad zur JSON-Datenbank
DATABASE_PATH = 'database/users.json'


def load_users():
    try:
        with open(DATABASE_PATH, 'r') as file:
            return pd.DataFrame(json.load(file)['users'])
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame(columns=['guid', 'username', 'email', 'pw_hash', 'first_name', 'last_name'])


def save_users(users_db):
    with open(DATABASE_PATH, 'w') as file:
        json.dump({"users": users_db.to_dict('records')}, file)


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def verify_user(email, password):
    users_db = load_users()
    user = users_db[users_db['email'] == email]
    if not user.empty and user.iloc[0]['pw_hash'] == hash_password(password):
        return True, user.iloc[0]['username']
    return False, ""


def register_user(username, email, password, first_name, last_name):
    users_db = load_users()
    if email not in users_db['email'].values:
        new_user = {'guid': 'new-guid', 'username': username, 'email': email, 'pw_hash': hash_password(password),
                    'first_name': first_name, 'last_name': last_name}
        updated_db = users_db.append(new_user, ignore_index=True)
        save_users(updated_db)
        return True
    return False


def main():
    st.title("Willkommen zur Anmeldung")
    menu = ["Home", "Login", "Sign Up", "Passwort vergessen"]
    choice = st.sidebar.selectbox("Menü", menu)

    if choice == "Home":
        st.subheader("Home Bereich")

    elif choice == "Login":
        st.subheader("Login Bereich")
        email = st.text_input("Email")
        password = st.text_input("Passwort", type='password')
        if st.button("Login"):
            authenticated, username = verify_user(email, password)
            if authenticated:
                st.success(f"Eingeloggt als {username}")
            else:
                st.warning("Ungültige Email/Passwort Kombination")

    elif choice == "Sign Up":
        st.subheader("Registrieren Sie sich")
        new_user_username = st.text_input("Benutzername")
        new_user_email = st.text_input("Email")
        new_user_password = st.text_input("Passwort", type='password')
        new_user_first_name = st.text_input("Vorname")
        new_user_last_name = st.text_input("Nachname")

        if st.button("Registrieren"):
            if register_user(new_user_username, new_user_email, new_user_password, new_user_first_name,
                             new_user_last_name):
                st.success(f"Konto für {new_user_email} wurde erfolgreich erstellt!")
            else:
                st.error("Ein Benutzer mit dieser E-Mail-Adresse existiert bereits.")

    elif choice == "Passwort vergessen":
        st.subheader("Passwort zurücksetzen")
        email = st.text_input("Bitte geben Sie Ihre E-Mail-Adresse ein, um Ihr Passwort zurückzusetzen.")
        if st.button("Passwort zurücksetzen"):
            users_db = load_users()
            if email in users_db['email'].values:
                st.success("Ein Link zum Zurücksetzen Ihres Passworts wurde an Ihre E-Mail gesendet.")
            else:
                st.error("Diese E-Mail-Adresse wurde nicht gefunden.")


if __name__ == '__main__':
    main()