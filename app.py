import os
import pickle
import pandas as pd
import streamlit as st
import requests

# Store API key securely (Replace this with an environment variable for production)
API_KEY = os.getenv("TMDB_API_KEY", "1d2604378a6d26a59096a2d0e0b46620")

# Get the absolute path of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
movies_path = os.path.join(BASE_DIR, "movies_dict.pkl")
similarity_path = os.path.join(BASE_DIR, "model_similarity.pkl")

# Load data safely
if not os.path.exists(movies_path):
    st.error(f"File '{movies_path}' not found. Please check the file path.")
    st.stop()

if not os.path.exists(similarity_path):
    st.error(f"File '{similarity_path}' not found. Please check the file path.")
    st.stop()

# Load movies dictionary and similarity matrix
movies_dictionary = pickle.load(open(movies_path, "rb"))
movies = pd.DataFrame(movies_dictionary)
similarity = pickle.load(open(similarity_path, "rb"))

# Function to fetch movie posters
def fetch_poster(movie_id):
    """Fetch the movie poster URL from TMDB API."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    response = requests.get(url)

    if response.status_code != 200:
        return "https://via.placeholder.com/500x750?text=No+Image"

    data = response.json()
    poster_path = data.get('poster_path')

    if not poster_path:
        return "https://via.placeholder.com/500x750?text=No+Image"

    return f"https://image.tmdb.org/t/p/w500/{poster_path}"

# Function to get movie recommendations
def recommend(movie):
    """Returns the top 10 recommended movies and their posters."""
    if movie not in movies['title'].values:
        return ["Movie not found in database."], []

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    # Get the top 10 most similar movies
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].get('movie_id', None)
        if movie_id:
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i[0]]['title'])

    return recommended_movie_names, recommended_movie_posters

# Streamlit UI
st.set_page_config(page_title="Movie Recommendation Engine", page_icon="🎬", layout="wide")

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🎬 Movie Recommendation Engine</h1>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center; color: #555;'>Find your next favorite movie! 🍿</h3>", unsafe_allow_html=True)

# Dropdown for movie selection
movie_name = st.selectbox("🎥 **Select a movie:**", movies['title'].values)

if st.button("✨ Get Recommendations"):
    with st.spinner("Finding the best movies for you... 🎥✨"):
        recommended_movies, recommended_posters = recommend(movie_name)

    if recommended_movies[0] == "Movie not found in database.":
        st.warning(recommended_movies[0])
    else:
        st.markdown(f"<h2 style='text-align: center; color: #FF914D;'>Top 10 recommendations for <strong>{movie_name}</strong>:</h2>", unsafe_allow_html=True)

        # Display recommendations in two rows (5 movies per row)
        with st.container():
            cols = st.columns(5)  # First row
            cols2 = st.columns(5)  # Second row

            for idx in range(10):
                if idx < len(recommended_movies):  # Prevent index errors
                    col = cols[idx] if idx < 5 else cols2[idx - 5]
                    with col:
                        st.markdown(f"<h4 style='text-align: center;'>{recommended_movies[idx]}</h4>", unsafe_allow_html=True)
                        st.image(recommended_posters[idx], use_container_width=True, caption=recommended_movies[idx])
