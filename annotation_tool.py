import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageOps

class AnnotationTool:
    def __init__(self, root, image_folder):
        self.root = root
        self.image_folder = image_folder
        self.label_folder = "labels"

        if not os.path.exists(self.label_folder):
            os.makedirs(self.label_folder)

        self.images = [f for f in os.listdir(image_folder) if f.endswith(('png', 'jpg', 'jpeg'))]
        self.current_image_index = 0

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(fill="both", expand=True)
        
        # Create vertical scrollbar
        self.canvas_vscrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical")
        self.canvas_vscrollbar.pack(side="right", fill="y")
        
        # Create horizontal scrollbar
        self.canvas_hscrollbar = tk.Scrollbar(self.canvas_frame, orient="horizontal")
        self.canvas_hscrollbar.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(self.canvas_frame, yscrollcommand=self.canvas_vscrollbar.set, xscrollcommand=self.canvas_hscrollbar.set)
        self.canvas.pack(fill="both", expand=True)
        self.canvas_vscrollbar.config(command=self.canvas.yview)
        self.canvas_hscrollbar.config(command=self.canvas.xview)

        self.load_image()

        self.start_x = self.start_y = 0
        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Left>", self.prev_image)

    def load_image(self):
        image_path = os.path.join(self.image_folder, self.images[self.current_image_index])
        try:
            with open(image_path, 'rb') as f:
                image = Image.open(f)
                image = ImageOps.exif_transpose(image)
                image = image.convert("RGB")

                self.tk_image = ImageTk.PhotoImage(master=self.root, image=image)
                self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
                self.canvas.config(scrollregion=self.canvas.bbox("all"))

                # Load saved bounding boxes if they exist
                self.display_saved_boxes()

        except Exception as e:
            messagebox.showerror("Error", f"Could not load image {image_path}: {e}")
            self.next_image(None)

    def display_saved_boxes(self):
        image_name = self.images[self.current_image_index]
        label_file_path = os.path.join(self.label_folder, f"{os.path.splitext(image_name)[0]}.txt")

        if os.path.exists(label_file_path):
            with open(label_file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    _, start_x, start_y, width, height = map(float, line.strip().split())
                    self.canvas.create_rectangle(start_x, start_y, start_x + width, start_y + height, outline="red")

    def on_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        start_x, end_x = min(self.start_x, end_x), max(self.start_x, end_x)
        start_y, end_y = min(self.start_y, end_y), max(self.start_y, end_y)

        width = end_x - start_x
        height = end_y - start_y

        if width > 0 and height > 0:  # Ensure valid bounding box dimensions
            label_id = simpledialog.askstring("Input", "Enter Label ID:")
            if label_id:  # Ensure the label is not empty
                image_name = self.images[self.current_image_index]
                label_file_path = os.path.join(self.label_folder, f"{os.path.splitext(image_name)[0]}.txt")
                print(label_file_path)
                with open(label_file_path, "a") as file:
                    file.write(f"{label_id} {start_x} {start_y} {width} {height}\n")
                self.next_image(None)
            else:
                messagebox.showwarning("Warning", "No label entered.")
                self.canvas.delete(self.rect)  # Remove the drawn bounding box if no label is entered

    def next_image(self, event):
        if self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self.canvas.delete("all")
            self.load_image()
        else:
            messagebox.showinfo("Info", "End of File")

    def prev_image(self, event):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.canvas.delete("all")
            self.load_image()

if __name__ == "__main__":
    image_folder = filedialog.askdirectory(title="Select Image Folder")
    if image_folder:
        root = tk.Tk()
        tool = AnnotationTool(root, image_folder)
        root.mainloop()


