import os
import urllib.request

def ensure_model_exists():
    model_dir = "models"
    model_path = os.path.join(model_dir, "u2net.onnx")
    
    # Direct download link to a public U2Net ONNX mirror (Hugging Face)
    url = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx" 
    # NOTE: If you have a specific U2Net URL you prefer, swap out the URL string above!

    # Create the models folder if it doesn't exist
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    # If the model is missing, download it automatically
    if not os.path.exists(model_path):
        print("Model file (u2net.onnx) not found locally.")
        print("Downloading model from server... This may take a couple of minutes.")
        try:
            # Download the file and save it to the models folder
            urllib.request.urlretrieve(url, model_path)
            print("Download complete! Model saved successfully.")
        except Exception as e:
            print(f"Error downloading the model: {e}")
            print("Please check your internet connection or URL.")
            raise e
    else:
        print("Model file detected. Skipping download.")

# Call this function at the very beginning of your application execution
if __name__ == "__main__":
    ensure_model_exists()
