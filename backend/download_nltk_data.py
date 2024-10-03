import nltk
import os

def download_nltk_data():
    # Set a custom download directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    nltk_data_dir = os.path.join(current_dir, 'nltk_data')
    os.makedirs(nltk_data_dir, exist_ok=True)

    # Set the NLTK_DATA environment variable
    os.environ['NLTK_DATA'] = nltk_data_dir

    # Add the custom directory to NLTK's data path
    nltk.data.path.append(nltk_data_dir)

    # Download required NLTK data
    nltk.download('stopwords', download_dir=nltk_data_dir, quiet=False)
    nltk.download('punkt', download_dir=nltk_data_dir, quiet=False)

    print(f"NLTK data downloaded successfully to {nltk_data_dir}")
    print(f"NLTK data path: {nltk.data.path}")

if __name__ == "__main__":
    download_nltk_data()