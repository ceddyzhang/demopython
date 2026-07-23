import os

import streamlit as st

# On Streamlit Community Cloud, secrets come from the Secrets panel (st.secrets),
# not a .env file (which is gitignored and never deployed). Locally, .env + dotenv
# populates os.environ directly. Bridging st.secrets into os.environ here means
# retrieve_case_studies.py's plain os.environ[...] lookups work in both places.
try:
    for _key in st.secrets:
        os.environ.setdefault(_key, str(st.secrets[_key]))
except Exception:
    pass  # no secrets.toml locally — fine, .env covers local dev instead

from retrieve_case_studies import get_connection, get_genai_client, retrieve

st.set_page_config(page_title="Business Case Study Finder", page_icon="🔍")


@st.cache_resource
def get_resources():
    return get_connection(), get_genai_client()


conn, genai_client = get_resources()

st.title("Business Case Study Finder")
st.caption(
    "Semantic search over a library of business case studies — finds analogous past "
    "situations even when the wording shares no keywords with your query."
)

example = (
    "a company relied too heavily on what made it successful in the past and was "
    "slow to respond when a cheaper, more convenient alternative won over customers"
)
query = st.text_input("Describe a business situation:", placeholder=example)

if st.button("Search", type="primary") or query:
    if query:
        with st.spinner("Searching..."):
            results = retrieve(query, conn, genai_client)

        st.subheader("Most analogous case studies")
        for filename, content, distance in results:
            similarity = 1 - distance
            with st.container(border=True):
                st.markdown(f"**{filename}**  \nsimilarity: `{similarity:.3f}`")
                st.write(content)
