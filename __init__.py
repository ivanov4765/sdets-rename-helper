import tkinter as tk
import os
from tkinter import filedialog, messagebox
from typing import Tuple, Any


class MainApplication(tk.Tk):
    files_map: dict = {}
    original_filenames_map: dict = {}
    scroll_bar_position = (0.0, 1.0)

    def reset_files_boxes(self):
        self.result_files_box.delete(0, tk.END)
        for item in self.files_map.keys():
            self.files_map[item] = item

    def show_items(self, list_of_items: list, target_box: tk.Listbox, check_original: bool):
        target_box.delete(0, tk.END)
        index = 0
        for item in list_of_items:
            target_box.insert(tk.END, item)
            if check_original and not self.files_map.get(item):
                self.source_files_box.itemconfig(index, {'fg': 'gray50'})
                target_box.itemconfig(index, {'fg': 'red'})
            elif check_original and self.files_map.get(item):
                self.source_files_box.itemconfig(index, {'fg': 'black'})
                target_box.itemconfig(index, {'fg': 'black'})
            index += 1
        ceva = ('moveto', self.scroll_bar_position[0])
        self.source_files_box.yview(*ceva)
        self.result_files_box.yview(*ceva)

    def rename_all_files(self, new_name):
        if self.rename_radio_value.get() == 2:
            items = self.source_files_box.curselection()
            for item in items:
                selected_filename = self.original_filenames_map.get(item)
                split_name = selected_filename.split("_", 1)
                if len(split_name) >= 1:
                    self.files_map[selected_filename] = new_name + "_" + split_name[1]
        else:
            for filename in self.files_map.keys():
                split_name = filename.split("_", 1)
                if len(split_name) >= 1:
                    self.files_map[filename] = new_name + "_" + split_name[1]

        self.show_items(self.files_map.values(), self.result_files_box, True)

    def reset_messages(self):
        self.error_message_label.configure(text="")
        self.output_message_label.configure(text="")

    def save_button_handler(self):
        current_dir = self.path_input_text_variable.get()
        renamed_files = 0
        for item in self.files_map:
            if item != self.files_map[item]:
                src = current_dir + "\\" + item
                dst = current_dir + "\\" + self.files_map[item]
                os.rename(src, dst)
                renamed_files += 1
        self.output_message_label.configure(text=str(renamed_files) + " files renamed!")
        self.build_files_box()

    def open_path_button(self):
        # Enter Path section
        if self.path_input_text_variable.get():
            current_directory_path = filedialog.askdirectory(parent=self.inputFrame,
                                                             initialdir=self.path_input_text_variable.get(),
                                                             title='Please select a directory')
        else:
            current_directory_path = filedialog.askdirectory(parent=self.inputFrame,
                                                             initialdir="/",
                                                             title='Please select a directory')
        if current_directory_path:
            self.path_input_text_variable.set(current_directory_path)
            self.build_files_box()

    def step_button(self, item_type, increment):
        def update_step(filename):
            selected_temp_filename = self.files_map.get(filename)
            split_name = selected_temp_filename.split("_", 2)
            if len(split_name) >= 2:
                sequence = int(split_name[1])

                if increment:
                    sequence += 1
                elif sequence > 0:
                    sequence -= 1

                if sequence < 10:
                    sequence_str = "_0" + str(sequence) + "_"
                else:
                    sequence_str = "_" + str(sequence) + "_"
            self.files_map[filename] = split_name[0] + sequence_str + split_name[2]

        if item_type == 'step':
            if self.rename_radio_value.get() == 2:
                items = self.source_files_box.curselection()
                for item in items:
                    selected_filename = self.original_filenames_map.get(item)
                    update_step(selected_filename)

            else:
                for filename in self.files_map.keys():
                    update_step(filename)


        self.show_items(self.files_map.values(), self.result_files_box, True)


    def build_files_box(self):
        # self.reset_messages()
        # Build a dictionary(originalFilename -> updatedFilename) from provided input
        try:
            self.files_map.clear()
            self.original_filenames_map.clear()
            index = 0
            for filename in os.listdir(self.path_input_text_variable.get()):
                self.files_map[filename] = filename
                if index == 0:
                    split_name = filename.split("_", 1)
                    self.name_input_text_variable.set(split_name[0])

                self.original_filenames_map[index] = filename
                index += 1

            self.show_items(self.files_map.keys(), self.source_files_box, False)
            self.show_items(self.files_map.values(), self.result_files_box, False)

        except FileNotFoundError:
            self.error_message_label.configure(text="Invalid Path provided")
            self.source_files_box.delete(0, tk.END)
            self.result_files_box.delete(0, tk.END)

    def build_input_frame(self):
        def enter_handler(event):
            self.build_files_box()

        def key_pressed_handler(event):
            new_name = self.name_input_text_variable.get()
            self.rename_all_files(new_name)

        def select_handler():
            self.reset_files_boxes()
            new_name = self.name_input_text_variable.get()
            self.rename_all_files(new_name)

        # Enter Path section
        path_label = tk.Label(self.inputFrame, text="Enter Path")
        path_label.grid(row=0, column=0, pady=(10, 0), padx=(10, 0))
        self.path_input_text_variable = tk.StringVar()
        self.path_input = tk.Entry(self.inputFrame, width=30, textvariable=self.path_input_text_variable)
        self.path_input.bind('<Return>', enter_handler)
        self.path_input.grid(row=0, column=1, pady=(10, 0), padx=(0, 0))
        tk.Button(self.inputFrame, text="browse", command=self.open_path_button, height=1).grid(row=0, column=2, pady=(10, 0), padx=(0, 0))

        # Enter Name section
        tk.Label(self.inputFrame, text="Enter Name").grid(row=0, column=3, pady=(10, 0), padx=(365, 0))
        self.name_input_text_variable = tk.StringVar()
        name_input = tk.Entry(self.inputFrame, width=30, textvariable=self.name_input_text_variable)
        name_input.grid(row=0, column=4, pady=(10, 0), padx=(10, 0))
        name_input.bind('<KeyRelease>', key_pressed_handler)

        # Rename all Radio Buttons
        self.rename_radio_value = tk.IntVar()
        tk.Label(self.inputFrame, text="Rename:").grid(row=1, column=3, pady=(0, 0), padx=(365, 0), sticky='e')
        tk.Radiobutton(self.inputFrame, text="All", variable=self.rename_radio_value,
                       value=1, command=lambda: select_handler()).grid(row=1, column=4, pady=(0, 0), padx=(10, 0), sticky='w')
        tk.Radiobutton(self.inputFrame, text="Selected", variable=self.rename_radio_value,
                       value=2, command=lambda: select_handler()).grid(row=2, column=4, pady=(0, 0), padx=(10, 0), sticky='w')
        self.rename_radio_value.set(1)

        tk.Button(self.inputFrame, text="Step-", command=lambda: self.step_button('step', False), height=1)\
            .grid(row=3, column=5, padx=(0, 0), pady=(0, 0))
        tk.Button(self.inputFrame, text="Step+", command=lambda: self.step_button('step', True), height=1)\
            .grid(row=3, column=6, padx=(0, 0), pady=(0, 0))
        tk.Button(self.inputFrame, text="cl-", command=lambda: self.step_button('cl', False), height=1)\
            .grid(row=3, column=7, padx=(10, 0), pady=(0, 0))
        tk.Button(self.inputFrame, text="cl+", command=lambda: self.step_button('cl', True), height=1)\
            .grid(row=3, column=8, padx=(0, 0), pady=(0, 0))
        tk.Button(self.inputFrame, text="en-", command=lambda: self.step_button('en', False), height=1)\
            .grid(row=3, column=9, padx=(10, 0), pady=(0, 0))
        tk.Button(self.inputFrame, text="en+", command=lambda: self.step_button('en', True), height=1)\
            .grid(row=3, column=10, padx=(0, 0), pady=(0, 0))
        tk.Button(self.inputFrame, text="i-", command=lambda: self.step_button('i', False), height=1)\
            .grid(row=3, column=11, padx=(10, 0), pady=(0, 0))
        tk.Button(self.inputFrame, text="i+", command=lambda: self.step_button('i', True), height=1)\
            .grid(row=3, column=12, padx=(0, 0), pady=(0, 0))

    def build_output_frame(self):
        def on_single_click_release(event):
            if self.rename_radio_value.get() == 2:
                self.reset_files_boxes()
                new_name = self.name_input_text_variable.get()
                self.rename_all_files(new_name)

        def yscroll1(*args):
            if self.result_files_box.yview() != self.source_files_box.yview():
                self.result_files_box.yview_moveto(args[0])
            self.source_files_scrollbar.set(*args)
            self.result_files_scrollbar.set(*args)
            self.scroll_bar_position = (args[0], args[1])

        def yscroll2(*args):
            if self.source_files_box.yview() != self.result_files_box.yview():
                self.source_files_box.yview_moveto(args[0])
            self.source_files_scrollbar.set(*args)
            self.result_files_scrollbar.set(*args)
            self.scroll_bar_position = (args[0], args[1])


        def yview(*args):
            self.source_files_box.yview(*args)
            self.result_files_box.yview(*args)

        # Before box - displaying original filenames
        self.source_files_box = tk.Listbox(self.outputFrame, width=100, height=45, selectmode=tk.EXTENDED,
                                           activestyle='none')
        self.source_files_box.grid(row=0, column=0, pady=10, padx=(10, 0))
        self.source_files_box.bind('<Double-Button-1>', self.on_double_click)
        self.source_files_box.bind('<ButtonRelease-1>', on_single_click_release)
        self.source_files_scrollbar = tk.Scrollbar(self.outputFrame, orient="vertical")
        self.source_files_scrollbar.grid(row=0, column=1, pady=10, sticky="nsw")
        self.source_files_scrollbar.config(command=yview)
        self.source_files_box.config(yscrollcommand=yscroll1)
        self.source_files_box.configure(exportselection=False)

        # '->' label between the 2 boxes
        # TODO: add a custom image instead of plain text
        tk.Label(self.outputFrame, text="->", anchor="center").grid(row=0, column=2, padx=(10, 0), sticky='nsew')

        # After box - displaying updated filenames
        self.result_files_box = tk.Listbox(self.outputFrame, width=100, height=45,
                                           selectmode=tk.SINGLE, selectbackground='white',
                                           selectforeground='black',
                                           activestyle='none')
        self.result_files_box.grid(row=0, column=3, pady=10, padx=(10, 0))
        self.result_files_box.bind('<Double-Button-1>', self.on_double_click)
        self.result_files_scrollbar = tk.Scrollbar(self.outputFrame, orient="vertical")
        self.result_files_scrollbar.grid(row=0, column=4, pady=10, sticky="nsw")
        self.result_files_scrollbar.config(command=yview)
        self.result_files_box.config(yscrollcommand=yscroll2)

    def build_messages_frame(self):
        self.output_message_label = tk.Label(self.messagesFrame, width=165, text="", anchor="w")
        self.output_message_label.grid(row=0, column=0, padx=10, sticky='w')

        self.error_message_label = tk.Label(self.messagesFrame, width=165, text="", anchor="w")
        self.error_message_label.grid(row=1, column=0, padx=10, sticky='w')
        tk.Button(self.messagesFrame, text="Save", command=self.save_button_handler)\
            .grid(row=0, column=2, pady=(10, 0), padx=(10, 10), sticky='e')

    def on_double_click(self, evt):
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        os.startfile(self.path_input.get() + '/' + value)

    def __init__(self):
        super().__init__()
        self.title("Welcome to SDETs rename helper")
        self.inputFrame = tk.Frame()
        self.outputFrame = tk.Frame()
        self.messagesFrame = tk.Frame()

        self.build_input_frame()
        self.build_output_frame()
        self.build_messages_frame()

        self.inputFrame.grid(row=0, column=0, sticky='nsew')
        self.outputFrame.grid(row=1, column=0, sticky='nsew')
        self.messagesFrame.grid(row=2, column=0, sticky='nsew')


MainApplication().mainloop()