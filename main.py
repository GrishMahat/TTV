from flask import Flask, request, jsonify

from src.TextToVideo import TextToVideo

app = Flask(__name)

@app.route('/convert_text_to_video', methods=['POST'])
def convert_text_to_video():
    try:
        text = request.form.get('text')
        output_file = request.form.get('output_file')

        if not text:
            return jsonify({'error': 'Input text is empty'})

        if not output_file:
            return jsonify({'error': 'Output file name is empty'})

        ttv = TextToVideo(text, output_file + '.mp4')
        ttv.process_video_elements()
        ttv.save_video()
        
        return jsonify({'message': 'Video saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
