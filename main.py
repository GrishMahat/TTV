from text_to_video import TextToVideo

def main():
    # Read the text from the file
    with open("test_script.txt", "r") as f:
        text = f.read().replace("\n", " ")
    
    # Create an instance of the TextToVideo class
    ttv = TextToVideo(text, "output.mp4")
    
    # Process the video elements and generate the video
    ttv.process_video_elements()
    
    # Save the video
    ttv.save_video()

if __name__ == "__main__":
    main()
