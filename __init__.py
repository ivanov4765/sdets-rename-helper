from tkinter import Tk, END, Listbox, Label, StringVar, Entry, Button, IntVar, Radiobutton, EXTENDED, Scrollbar, SINGLE, Frame
from os import listdir, system, environ, rename, startfile, getcwd, path
from tkinter import filedialog, messagebox
from sys import argv


class MainApplication(Tk):
    files_map: dict = {}
    original_filenames_map: dict = {}
    scroll_bar_position = (0.0, 1.0)
    cmd_args = "/k"

    def get_all_files(self, files_path):
        for file in listdir(files_path):
            if path.isfile(path.join(files_path, file)):
                yield file

    def reset_files_boxes(self):
        self.result_files_box.delete(0, END)
        for item in self.files_map.keys():
            self.files_map[item] = item

    def show_items(self, list_of_items: list, target_box: Listbox, check_original: bool):
        target_box.delete(0, END)
        index = 0
        for item in list_of_items:
            target_box.insert(END, item)
            if check_original and not self.files_map.get(item):
                self.source_files_box.itemconfig(index, {'fg': 'gray50'})
                target_box.itemconfig(index, {'fg': 'red'})
            elif check_original and self.files_map.get(item):
                self.source_files_box.itemconfig(index, {'fg': 'black'})
                target_box.itemconfig(index, {'fg': 'black'})
            index += 1
        scroll_position = ('moveto', self.scroll_bar_position[0])
        self.source_files_box.yview(*scroll_position)
        self.result_files_box.yview(*scroll_position)

    def run_test_button(self):
        if 'TestTool' in environ:
            if self.path_input_text_variable.get():
                test_tool_path = environ.get('TestTool').replace("\\", "\\\\")
                system("start \"\" cmd " + self.cmd_args + " \"cd /D " + test_tool_path + "  & test.bat run \""
                          + self.path_input_text_variable.get().replace("/", "\\") + "\" \"")
        else:
            self.error_message_label.configure(text="Error Running the test. 'TestTool' environment variable is not set.")

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
        files_to_rename = 0
        for item in self.files_map:
            if item != self.files_map[item]:
                files_to_rename += 1
        if files_to_rename > 0:
            if messagebox.askyesno('Rename Confirmation',
                                   'Do you really want to rename ' + str(files_to_rename) + ' files?'):
                files_not_renamed = 0
                current_dir = self.path_input_text_variable.get()
                renamed_files = 0
                for item in self.files_map:
                    if item != self.files_map[item]:
                        src = current_dir + "\\" + item
                        dst = current_dir + "\\" + self.files_map[item]
                        try:
                            rename(src, dst)
                            renamed_files += 1
                        except FileExistsError:
                            files_not_renamed += 1
                self.output_message_label.configure(text=str(renamed_files) + " files successfully renamed!")
                self.build_files_box()
                if files_not_renamed > 0:
                    self.error_message_label.configure(text="Cannot rename " + str(files_not_renamed)
                                                            + " file(s). File already exists!")
            else:
                self.reset_messages()
        else:
            self.error_message_label.configure(text="Nothing to rename!")

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

        def update_index(filename, index_to_update):
            selected_temp_filename = self.files_map.get(filename)

            if selected_temp_filename.find(index_to_update) > 0:
                start_position = selected_temp_filename.find(index_to_update) + len(index_to_update)
                index_len = 3
                sequence = 0
                while index_len > 0:
                    try:
                        sequence = int(selected_temp_filename[start_position: start_position + index_len])
                        break
                    except ValueError:
                        index_len -= 1

                if increment:
                    sequence += 1
                elif sequence > 0:
                    sequence -= 1

                self.files_map[filename] = selected_temp_filename.replace(
                    selected_temp_filename[selected_temp_filename.find(index_to_update): start_position + index_len]
                    , index_to_update + str(sequence)
                    , 1)

        if item_type == 'step':
            if self.rename_radio_value.get() == 2:
                items = self.source_files_box.curselection()
                for item in items:
                    selected_filename = self.original_filenames_map.get(item)
                    update_step(selected_filename)

            else:
                for filename in self.files_map.keys():
                    update_step(filename)
        else:
            if self.rename_radio_value.get() == 2:
                items = self.source_files_box.curselection()
                for item in items:
                    selected_filename = self.original_filenames_map.get(item)
                    update_index(selected_filename, item_type)

            else:
                for filename in self.files_map.keys():
                    update_index(filename, item_type)

        self.show_items(self.files_map.values(), self.result_files_box, True)

    def build_files_box(self):
        self.reset_messages()
        # Build a dictionary(originalFilename -> updatedFilename) from provided input
        try:
            self.files_map.clear()
            self.original_filenames_map.clear()
            index = 0
            for filename in self.get_all_files(self.path_input_text_variable.get()):
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
            self.source_files_box.delete(0, END)
            self.result_files_box.delete(0, END)

        except FileExistsError:
            self.error_message_label.configure(text="Cannot create a file when that file already exists")

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
        path_label = Label(self.inputFrame, text="Enter Files Path: ")
        path_label.grid(row=0, column=0, pady=(10, 0), padx=(10, 0), sticky='w')
        self.path_input_text_variable = StringVar()
        self.path_input = Entry(self.inputFrame, width=30, textvariable=self.path_input_text_variable)
        self.path_input.bind('<Return>', enter_handler)
        self.path_input.grid(row=0, column=1, pady=(10, 0), padx=(0, 0), sticky='w')
        Button(self.inputFrame, text="browse", command=self.open_path_button, height=1).grid(row=0, column=2,
                                                                                                pady=(10, 0),
                                                                                                padx=(0, 0), sticky='w')

        # Enter Name section
        Label(self.inputFrame, text="Enter Name:").grid(row=0, column=4, pady=(10, 0), padx=(30, 0), sticky='e')
        self.name_input_text_variable = StringVar()
        name_input = Entry(self.inputFrame, width=30, textvariable=self.name_input_text_variable)
        name_input.grid(row=0, column=5, columnspan=2, pady=(10, 0), padx=(10, 0))
        name_input.bind('<KeyRelease>', key_pressed_handler)

        # Rename all Radio Buttons
        self.rename_radio_value = IntVar()
        Label(self.inputFrame, text="Rename:").grid(row=1, column=4, pady=(0, 0), padx=(0, 0), sticky='e')
        Radiobutton(self.inputFrame, text="All", variable=self.rename_radio_value,
                       value=1, command=lambda: select_handler()) \
            .grid(row=1, column=5, pady=(0, 0), padx=(10, 0), sticky='w')
        Radiobutton(self.inputFrame, text="Selected", variable=self.rename_radio_value,
                       value=2, command=lambda: select_handler()) \
            .grid(row=1, column=6, pady=(0, 0), padx=(0, 0), sticky='w')
        self.rename_radio_value.set(1)

        Button(self.inputFrame, text="Run Test", command=lambda: self.run_test_button(), height=1, width=12) \
            .grid(row=2, column=0, padx=(10, 0), pady=(0, 0))
        Button(self.inputFrame, text="Step-", command=lambda: self.step_button('step', False), height=1) \
            .grid(row=2, column=7, padx=(0, 0), pady=(0, 0))
        Button(self.inputFrame, text="Step+", command=lambda: self.step_button('step', True), height=1) \
            .grid(row=2, column=8, padx=(0, 0), pady=(0, 0))
        Button(self.inputFrame, text="cl-", command=lambda: self.step_button('_cl', False), height=1) \
            .grid(row=2, column=9, padx=(10, 0), pady=(0, 0))
        Button(self.inputFrame, text="cl+", command=lambda: self.step_button('_cl', True), height=1) \
            .grid(row=2, column=10, padx=(0, 0), pady=(0, 0))
        Button(self.inputFrame, text="en-", command=lambda: self.step_button('_en', False), height=1) \
            .grid(row=2, column=11, padx=(10, 0), pady=(0, 0))
        Button(self.inputFrame, text="en+", command=lambda: self.step_button('_en', True), height=1) \
            .grid(row=2, column=12, padx=(0, 0), pady=(0, 0))
        Button(self.inputFrame, text="i-", command=lambda: self.step_button('_i', False), height=1) \
            .grid(row=2, column=13, padx=(10, 0), pady=(0, 0))
        Button(self.inputFrame, text="i+", command=lambda: self.step_button('_i', True), height=1) \
            .grid(row=2, column=14, padx=(0, 0), pady=(0, 0))

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
        Label(self.outputFrame, text="Before:").grid(row=0, column=0, pady=(5, 0), padx=(10, 0), sticky='w')
        self.source_files_box = Listbox(self.outputFrame, selectmode=EXTENDED,
                                           activestyle='none')
        self.source_files_box.grid(row=1, column=0, pady=5, padx=(15, 0), sticky="nsew")
        self.source_files_box.bind('<Double-Button-1>', self.on_double_click)
        self.source_files_box.bind('<ButtonRelease-1>', on_single_click_release)
        self.source_files_scrollbar = Scrollbar(self.outputFrame, orient="vertical")
        self.source_files_scrollbar.grid(row=1, column=1, pady=5, sticky="nsw")
        self.source_files_scrollbar.config(command=yview)
        self.source_files_box.config(yscrollcommand=yscroll1)
        self.source_files_box.configure(exportselection=False)

        # '->' label between the 2 boxes
        # TODO: add a custom image instead of plain text
        Label(self.outputFrame, text="->", anchor="center").grid(row=1, column=2, padx=(10, 0), sticky='nsew')

        # After box - displaying updated filenames
        Label(self.outputFrame, text="After:").grid(row=0, column=3, pady=(5, 0), padx=(10, 0), sticky='w')
        self.result_files_box = Listbox(self.outputFrame,
                                           selectmode=SINGLE, selectbackground='white',
                                           selectforeground='black',
                                           activestyle='none')
        self.result_files_box.grid(row=1, column=3, pady=5, padx=(10, 0), sticky="nsew")
        self.result_files_box.bind('<Double-Button-1>', self.on_double_click)
        self.result_files_scrollbar = Scrollbar(self.outputFrame, orient="vertical")
        self.result_files_scrollbar.grid(row=1, column=4, pady=5, padx=(0, 15), sticky="nsw")
        self.result_files_scrollbar.config(command=yview)
        self.result_files_box.config(yscrollcommand=yscroll2)

    def build_messages_frame(self):
        self.output_message_label = Label(self.messagesFrame, text="", anchor="w")
        self.output_message_label.grid(row=0, column=0, padx=5, sticky='w')

        self.error_message_label = Label(self.messagesFrame, text="", anchor="w", fg="red")
        self.error_message_label.grid(row=1, column=0, padx=5, sticky='w')
        Button(self.messagesFrame, text="Refresh", command=self.build_files_box, width=8) \
            .grid(row=0, column=1, pady=(5, 0), padx=(0, 0), sticky='nsew')

        Button(self.messagesFrame, text="Save", command=self.save_button_handler, width=8) \
            .grid(row=0, column=2, pady=(5, 0), padx=(5, 15), sticky='nsew')

    def on_double_click(self, evt):
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        startfile(self.path_input.get() + '/' + value)

    def __init__(self):
        super().__init__()
        self.title("SDETs rename helper")
        self.inputFrame = Frame()
        self.outputFrame = Frame()
        self.messagesFrame = Frame()
        self.minsize(900, 400)

        self.geometry("1250x700")

        self.build_input_frame()
        self.build_output_frame()
        self.build_messages_frame()

        self.path_input_text_variable.set(getcwd())
        self.build_files_box()

        if len(argv) > 2 and argv[2]:
            self.cmd_args = argv[2]

        self.inputFrame.grid(row=0, column=0, sticky='nsew')
        self.outputFrame.grid(row=1, column=0, sticky='nsew')
        self.messagesFrame.grid(row=2, column=0, sticky='nsew')

        self.inputFrame.columnconfigure(0, weight=1)
        self.inputFrame.columnconfigure(1, weight=1)
        self.inputFrame.columnconfigure(2, weight=1)
        self.inputFrame.columnconfigure(3, weight=90, minsize=120)
        self.inputFrame.columnconfigure(4, weight=1)
        self.inputFrame.columnconfigure(5, weight=1)
        self.inputFrame.columnconfigure(6, weight=1)
        self.inputFrame.columnconfigure(7, weight=1)
        self.inputFrame.columnconfigure(8, weight=1)
        self.inputFrame.columnconfigure(9, weight=1)
        self.inputFrame.columnconfigure(10, weight=1)
        self.inputFrame.columnconfigure(11, weight=1)
        self.inputFrame.columnconfigure(12, weight=1)
        self.inputFrame.columnconfigure(13, weight=1)
        self.inputFrame.columnconfigure(14, weight=1)
        self.inputFrame.rowconfigure(0, weight=1)
        self.inputFrame.rowconfigure(1, weight=1)
        self.inputFrame.rowconfigure(2, weight=1)


        self.outputFrame.columnconfigure(0, weight=50)
        self.outputFrame.columnconfigure(1, weight=1)
        self.outputFrame.columnconfigure(2, weight=1)
        self.outputFrame.columnconfigure(3, weight=50)
        self.outputFrame.columnconfigure(4, weight=1)
        self.outputFrame.rowconfigure(0, weight=1)
        self.outputFrame.rowconfigure(1, weight=50)

        self.messagesFrame.columnconfigure(0, weight=50)
        self.messagesFrame.columnconfigure(1, weight=1)
        self.messagesFrame.columnconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=50)
        self.rowconfigure(2, weight=1)


MainApplication().mainloop()
