# TTV

TTV is a Python application that processes custom text input to generate videos. It supports various features such as image search, voice-over, and video composition. With TTv, you can easily create video segments based on text input and generate engaging videos with dynamic images and voice narration.

## Features

- **Text Processing**: TTV processes custom text input and splits it into video segments based on the [IMAGE] tag.
- **Image Search**: It searches for images based on keywords specified in the text and selects a random set of images for each video segment.
- **Voice-over**: TTv provides support for voice narration by processing [VOICE] tags in the text and assigning the appropriate voice to each segment.
- **Video Composition**: It combines the selected images and voice-over to generate a final video segment.

## Requirements

- Python 3.7 or higher
- Dependencies (can be installed using `pip install -r requirements.txt`)

## Installation

1. Clone the repository: `git clone https://github.com/GrishMahat/TTV.git`

2. Navigate to the project directory: `cd TTV`


3. Install the dependencies: `pip install -r requirements.txt`



## Usage

1. Update the text input in the `test_script.txt` file with your desired content. You can add [IMAGE] tags to specify image keywords and [VOICE] tags to assign specific voices for voice-over.

2. Run the `main.py` script to process the text and generate the video:

python main.py


3. The generated video segments will be saved in the `output` directory. You can customize the output directory by modifying the `output_directory` variable in `main.py`.

## Configuration

You can customize the behavior of TTv by modifying the following variables in `main.py`:

- `IMAGE_SEARCH_COUNT`: Specifies the number of images to be selected for each video segment. You can adjust this value based on your preferences.
- `VIDEO_FPS`: Sets the frames per second (FPS) of the generated video. By default, it is set to 24 FPS, but you can modify it as per your requirements.
- `OUTPUT_DIRECTORY`: Specifies the directory where the generated video segments will be saved. By default, it is set to the `output` directory.

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.




