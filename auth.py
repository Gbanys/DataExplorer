import streamlit as st
import streamlit_authenticator as stauth

import streamlit as st
import time
import streamlit_authenticator as stauth
from streamlit_cookies_controller import CookieController

from database.database_functions import find_user_by_credentials, validate_access_token

def authenticate(controller: CookieController):

    token = controller.get('session')

    if not token:

        st.title("Login")

        user_name = st.text_input("Username", key="username")
        password = st.text_input("Password", key="password")

        if st.button("Login"):
            if not user_name:
                st.error("Please enter your username")
                st.stop()
            if not password:
                st.error("Please enter your password")
                st.stop()

            user = find_user_by_credentials(user_name, password)

            if user:
                controller.set(name='session', value=user.access_token, expires=user.access_token_expiration)
                time.sleep(2)
                st.rerun()
            else:
                st.write("Sorry, we couldn't find a user with those credentials.")
                st.stop()

        st.stop()
    else:
        user = validate_access_token(token)
        if user:
            return user
        else:
            controller.remove("session")
            st.rerun()


def logout(controller: CookieController):
    token = controller.get('session')
    if token:
        controller.remove('session')
        st.rerun()

