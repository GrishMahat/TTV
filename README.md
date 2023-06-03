# Video Generation Script

This script processes custom text input and generates videos based on the provided instructions. It supports various tags for image insertion and voice-over narration.

## Prerequisites

- Python 3.x
- Required Python packages (specified in requirements.txt)

## Installation

1. Clone the repository: `git clone https://github.com/your_username/video-generation-script.git`
2. Navigate to the project directory: `cd video-generation-script`
3. Install the required packages: `pip install -r requirements.txt`

## Usage

1. Prepare your custom text input in a file (e.g., `input.txt`) following the supported tags and format.
2. Run the script: `python main.py input.txt`
3. The script will process the input text, generate video segments, and combine them into a final video.
4. The generated video will be saved as `output.mp4` in the project directory.

## Customization

- Modify the `TextProcessor` class in `text_processor.py` to support additional tags or customize the text processing logic.
- Customize the `VideoSegment` class in `video_segment.py` to adjust the video generation process, image search, audio settings, etc.
- Feel free to explore and modify other classes and modules based on your specific requirements.

## Examples

- Example input text:
