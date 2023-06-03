from TextToVideo import TextToVideo

def main():
    # Read the text from the file
    with open("test_script.txt", "r") as f:
        text = f.read()
    
    # Remove newlines and replace them with spaces
    text = text.replace("\n", " ")
    
    # Create an instance of the TextToVideo class
    ttv = TextToVideo(text, "anime.mp4")
    
    # Generate the video
    ttv.generate_video()
    
    # Save the video
    ttv.save_video()

if __name__ == "__main__":
    main()
