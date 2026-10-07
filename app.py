import difflib
import pickle

import streamlit as st

# ---------------- CONFIG ----------------
MOVIES_PATH = "movies_data.pkl"
SIMILARITY_PATH = "similarity.pkl"
TOP_N = 5
# ----------------------------------------


@st.cache_resource
def load_data():
    with open(MOVIES_PATH, "rb") as f:
        movies_data = pickle.load(f)
    with open(SIMILARITY_PATH, "rb") as f:
        similarity = pickle.load(f)
    return movies_data, similarity


def recommend(movie_name, movies_data, similarity, top_n=TOP_N):
    list_of_all_titles = movies_data["title"].tolist()
    find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)

    if not find_close_match:
        return None, []

    close_match = find_close_match[0]
    index_of_movie = movies_data[movies_data.title == close_match]["index"].values[0]

    similarity_score = list(enumerate(similarity[index_of_movie]))
    sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)

    results = []
    for movie in sorted_similar_movies[1 : top_n + 1]:  # skip index 0, it's the movie itself
        idx = movie[0]
        row = movies_data[movies_data.index == idx].iloc[0]
        results.append(row)

    return close_match, results


st.set_page_config(page_title="Movie Recommender", page_icon="🎬")
st.title("🎬 Movie Recommender")
st.write("Type a movie you like, and get similar movies recommended.")

movies_data, similarity = load_data()

movie_name = st.text_input("Enter a movie name")

if st.button("Recommend") and movie_name.strip():
    with st.spinner("Finding similar movies..."):
        close_match, results = recommend(movie_name, movies_data, similarity)

    if close_match is None:
        st.error("No close match found. Try checking the spelling or a different title.")
    else:
        if close_match.lower() != movie_name.strip().lower():
            st.caption(f"Showing results for: **{close_match}**")

        st.subheader("Movies suggested for you")
        for row in results:
            with st.container():
                st.markdown(f"### {row['title']}")
                meta = []
                if "release_date" in row and row["release_date"]:
                    meta.append(str(row["release_date"])[:4])
                if "vote_average" in row:
                    meta.append(f"⭐ {row['vote_average']}")
                if "genres" in row and row["genres"]:
                    meta.append(str(row["genres"]))
                if meta:
                    st.caption(" · ".join(meta))
                if "overview" in row and isinstance(row["overview"], str):
                    st.write(row["overview"])
                st.divider()
