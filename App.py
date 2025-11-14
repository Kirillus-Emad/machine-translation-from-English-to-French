import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from utils import translate_text, load_models

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("English to French Translator")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Set up the style
        self.setup_style()
        
        # Load models in background
        self.load_models_async()
        
        # Create UI
        self.create_widgets()
    
    def setup_style(self):
        """Set up the application style"""
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
    
    def load_models_async(self):
        """Load models in a separate thread to avoid freezing the GUI"""
        def load():
            success = load_models()
            if success:
                self.status_label.config(text="Models loaded successfully! Ready to translate.")
            else:
                self.status_label.config(text="Error loading models. Please check file paths.")
        
        threading.Thread(target=load, daemon=True).start()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="English to French Translator", 
                               style='Header.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Input label
        input_label = ttk.Label(main_frame, text="Enter English text:")
        input_label.grid(row=1, column=0, sticky=tk.NW, padx=(0, 10))
        
        # Input text area
        self.input_text = scrolledtext.ScrolledText(main_frame, width=40, height=8,
                                                   font=('Arial', 10))
        self.input_text.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Translate button
        self.translate_button = ttk.Button(main_frame, text="Translate", 
                                          command=self.translate)
        self.translate_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Output label
        output_label = ttk.Label(main_frame, text="French translation:")
        output_label.grid(row=3, column=0, sticky=tk.NW, padx=(0, 10))
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(main_frame, width=40, height=8,
                                                    font=('Arial', 10), state=tk.DISABLED)
        self.output_text.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Loading models...")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # Bind Enter key to translate
        self.root.bind('<Return>', lambda event: self.translate())
    
    def translate(self):
        """Handle translation in a separate thread"""
        input_text = self.input_text.get("1.0", tk.END).strip()
        
        if not input_text:
            messagebox.showwarning("Input Error", "Please enter some text to translate.")
            return
        
        # Disable button and show loading
        self.translate_button.config(state=tk.DISABLED)
        self.status_label.config(text="Translating...")
        
        def do_translation():
            try:
                translated_text = translate_text(input_text)
                self.root.after(0, self.update_output, translated_text)
            except Exception as e:
                self.root.after(0, self.show_error, str(e))
        
        threading.Thread(target=do_translation, daemon=True).start()
    
    def update_output(self, translated_text):
        """Update the output text area with translation result"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", translated_text)
        self.output_text.config(state=tk.DISABLED)
        self.translate_button.config(state=tk.NORMAL)
        self.status_label.config(text="Translation complete!")
    
    def show_error(self, error_message):
        """Show error message"""
        messagebox.showerror("Translation Error", error_message)
        self.translate_button.config(state=tk.NORMAL)
        self.status_label.config(text="Error occurred during translation")

def main():
    root = tk.Tk()
    app = TranslationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()