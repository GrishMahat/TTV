import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from TextToVideo import TextToVideo

def choose_input_file() -> str:
    """Prompts the user to choose an input file and returns its path."""
    Tk().withdraw()  # Hide the Tkinter root window
    filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
    input_file = askopenfilename(filetypes=filetypes)
    return input_file

def main():
    # Select the input file
    input_file = choose_input_file()
    if not input_file:
        print("No input file selected. Exiting...")
        return

    with open(input_file, "r") as f:
        text = f.read().replace("\n", " ")

    # Customize the output file name
    output_file = input("Enter the desired output file name (without extension): ")
    output_file = output_file.strip()
    if not output_file:
        output_file = os.path.splitext(os.path.basename(input_file))[0] + ".mp4"
    else:
        output_file += ".mp4"

    # Create an instance of the TextToVideo class
    ttv = TextToVideo(text, output_file)

    try:
        # Process the video elements and generate the video
        ttv.process_video_elements()

        # Save the video
        ttv.save_video()
        print(f"Video saved as '{output_file}'.")

    except Exception as e:
        print(f"Error occurred while generating video: {str(e)}")

if __name__ == "__main__":
    main()
