import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.filedialog import askopenfilename

from src.TextToVideo import TextToVideo

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


class TextToVideoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Video Converter")

        self.input_text = tk.Text(root, height=10, width=40)
        self.input_text.pack(padx=20, pady=(20, 10))

        self.select_file_button = tk.Button(root, text="Select Input File", command=self.choose_input_file)
        self.select_file_button.pack(pady=10)

        self.output_file_label = tk.Label(root, text="Output File Name (without extension):")
        self.output_file_label.pack()

        self.output_file_entry = tk.Entry(root, width=40)
        self.output_file_entry.pack()
        self.convert_button = tk.Button(root, text="Convert", command=self.convert)
        self.convert_button.pack(pady=10)

    def choose_input_file(self):
        filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
        input_file = filedialog.askopenfilename(filetypes=filetypes)
        if input_file:
            with open(input_file, "r") as f:
                text = f.read()
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, text)

    def convert(self):
        text = self.input_text.get("1.0", tk.END).strip()
        output_file = self.output_file_entry.get().strip()
        if not text:
            messagebox.showerror("Error", "Input text is empty.")
            return
        if not output_file:
            messagebox.showerror("Error", "Output file name is empty.")
            return

        try:
            ttv = TextToVideo(text, output_file + ".mp4")
            ttv.process_video_elements()
            ttv.save_video()
            messagebox.showinfo("Success", f"Video saved as '{output_file}.mp4'.")
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred: {str(e)}")


def main():
    root = tk.Tk()
    app = TextToVideoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
