import os
import shutil
import requests
import re
import configparser

# Read configuration from the config file
config = configparser.ConfigParser()
config.read('config.ini')

# Retrieve the API key from the config file
api_key = config.get('API', 'OMDB_API_KEY')

# Retrieve the source directory from the config file
source_directory = config.get('Directories', 'SourceDirectory')

# Retrieve the destination directory from the config file
destination_directory = config.get('Directories', 'DestinationDirectory')

# Retrieve the video file types from the config file
video_file_types = tuple(config.get('Directories', 'VideoFileTypes').split(','))

# Function to get movie details from OMDB API
def get_movie_details(movie_title, year):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    url = f"http://www.omdbapi.com/?apikey={api_key}&t={movie_title}&y={year}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"API request failed with status code {response.status_code}")
        return None
    data = response.json()
    if data['Response'] == 'False':
        return None
    return data

# Function to process files in a given directory
def process_files(directory):
    # Iterate over each file/folder in the directory
    for name in os.listdir(directory):
        path = os.path.join(directory, name)

        # If it's a file and the file extension is in the video file types
        if os.path.isfile(path) and name.lower().endswith(video_file_types):
            # Extract the movie title and year from the folder/file name using regular expressions
            pattern = r'(.+?)(?:\s|\.)((?:19|20)\d{2})'
            match = re.search(pattern, name)
            if match:
                movie_title = match.group(1).strip()
                year = match.group(2).strip()
            else:
                # If year not found, set it to an empty string
                movie_title = name
                year = ''

            # Get movie details from OMDB API
            movie_details = get_movie_details(movie_title, year)

            if movie_details is None:
                print(f"Movie details not found for {movie_title} ({year})")
                continue

            # Extract genre from the movie details
            genre = movie_details["Genre"].split(",")[0]

            # Create a directory name using the movie title, year, and quality
            directory_name = f"{movie_title} ({year})" if year else movie_title

            # Define the destination directory path based on the destination directory, genre, and directory name
            destination_directory_path = os.path.join(destination_directory, genre)

            # Create the destination directory if it doesn't exist
            os.makedirs(destination_directory_path, exist_ok=True)

            # Check if the movie folder is already sorted in the respective genre folder
            if os.path.dirname(path) == destination_directory_path:
                print(f"Movie folder '{name}' is already sorted. Skipping...")
                continue

            # Check if the movie folder already exists in the destination directory
            destination_path = os.path.join(destination_directory_path, directory_name)
            if os.path.exists(destination_path):
                print(f"Movie folder '{name}' already exists in the destination directory. Skipping...")
                continue

            # Move the entire folder to the destination directory
            shutil.move(os.path.dirname(path), destination_directory_path)

            print(f"Moved {name} and its containing folder to {destination_directory_path}")

        # If it's a directory, recursively process its contents
        elif os.path.isdir(path):
            process_files(path)

# Start processing files from the source directory
process_files(source_directory)

print("Movie sorting completed!")
