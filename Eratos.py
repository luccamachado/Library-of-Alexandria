import tkinter
import datetime
import matplotlib
import os
import sys
import math
import shutil
import random


def main():
    root = Eratos()
    root.FileManager()
    root.mainloop()


def str_to_class(class_name):
    return getattr(sys.modules[__name__], class_name)


def read_dict(name):
    dictionary = {}

    dict_path = os.path.dirname(os.path.realpath(__file__)) + "/dicts"
    dicts = [f for f in os.listdir(dict_path) if f.endswith('.txt')]

    dict_check = 0
    for i in range(len(dicts)):
        if dicts[i].rstrip(".txt") == name:
            dict_check = 1

    if len(dicts) > 0:
        if dict_check == 1:
            txt = open(dict_path + "/" + name + ".txt", "r")
            file = txt.readlines()
            txt.close()

            for p in range(len(file)):
                item = file[p].split(":")
                dictionary[item[0]] = item[1].strip()

    return dictionary


class Eratos(tkinter.Tk):
    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        self.grid_propagate(0)
        self.winfo_toplevel().title("Eratos")
        self.container = None

        self.side1 = None
        self.side2 = None

    def FileManager(self):
        self.container = tkinter.Frame(self, bg="red")
        self.container.pack(side="top", fill="both", expand=True)

        self.side1 = int(self.winfo_screenwidth() / 2)
        self.side2 = int(self.winfo_screenheight() / 2)

        self.geometry("{0}x{1}+{2}+{3}".format(self.side1, self.side2, int(self.side1 / 2),  int(self.side2 / 2)))

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=4, uniform=1)
        self.container.columnconfigure(1, weight=1, uniform=1)
        self.container.columnconfigure(2, weight=4, uniform=1)

        self.container.file_list = FileList(self.container, self.container)
        self.container.engine_list = EngineList(self.container, self.container)

        self.container.file_list.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=1)
        self.container.engine_list.grid(row=0, column=2, sticky="nsew", rowspan=2, columnspan=1)


class FileList(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent, bg="black", bd=0, relief="ridge")
        self.grid_propagate(0)
        self.controller = controller

        self.text = tkinter.Text(self, bg="black", fg="white", font="Terminal, 12", selectbackground="grey", bd=2,
                                 pady=2, highlightbackground="white", highlightthickness=0, wrap="none",
                                 insertbackground="white", relief="ridge", state="disabled")

        self.button_filter = tkinter.Button(self, text="Filter", activebackground="grey", pady=5,
                                                      bg="black",
                                                      fg="white", highlightbackground="black", width=5, relief="ridge",
                                                      command=lambda: print("filter"))

        self.rowconfigure(0, weight=1, uniform=1)
        self.rowconfigure(1, weight=4, uniform=1)
        self.rowconfigure(2, weight=1, uniform=1)
        self.rowconfigure(3, weight=62, uniform=1)
        self.rowconfigure(4, weight=1, uniform=1)
        self.columnconfigure(0, weight=1, uniform=1)
        self.columnconfigure(1, weight=30, uniform=1)
        self.columnconfigure(2, weight=1, uniform=1)

        self.button_filter.grid(row=1, column=1, sticky="nsew")
        self.text.grid(row=3, column=1, sticky="nsew")

        self.get_files()

        self.text.bind("<Button-2>", (lambda event: self.highlight_selectedline()))
        self.text.bind("<Double-Button-1>", (lambda event: self.show_content()))

    def highlight_selectedline(self):
        check_1 = 0
        check_2 = (self.text.get("current linestart", "current lineend") != "")

        if len(self.text.tag_names("current")) > 0:
            if self.text.tag_names("current")[0] == "sel":
                check_1 = 1

            if check_2 is True:
                if self.text.tag_configure(self.text.tag_names("current")[check_1])["background"][4] == "red":
                    self.text.tag_configure(self.text.tag_names("current")[check_1], background="black")
                else:
                    self.text.tag_configure(self.text.tag_names("current")[check_1], background="red")

    def get_files(self):
        # Add Search Filters and Ordering of Results
        lst = []

        files_path = os.path.dirname(os.path.realpath(__file__)) + "/files"
        files = [f for f in os.listdir(files_path) if f.endswith('.txt')]

        for f in files:
            lst.append(f.rstrip(".txt"))

        self.insert_files(lst)

    def insert_files(self, lst):
        self.clear_text()

        self.text.tag_configure("selected_line", background="black")

        self.text["state"] = "normal"
        for f in range(len(lst)):
            self.text.insert("end", lst[f] + "\n")
            self.text.see("end")
            self.text.tag_add(lst[f], str(float(f + 1)) + " linestart", str(float(f + 1)) + " lineend+1c")
        self.text["state"] = "disabled"

    def clear_text(self):
        self.text["state"] = "normal"
        self.text.delete('1.0', tkinter.END)
        self.text["state"] = "disabled"

    def show_content(self):
        check_1 = 0
        if self.text.tag_names("current")[0] == "sel":
            check_1 = 1
        key = self.text.tag_names("current")[check_1]

        popup = TextPopup(self, self.controller, key)
        popup.read_file()
        self.controller.master.wait_window(popup)


class EngineList(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent, bg="black", bd=0, relief="ridge")
        self.grid_propagate(0)
        self.controller = controller

        self.progress_menu = None

        self.text = tkinter.Text(self, bg="black", fg="white", font="Terminal, 12", selectbackground="grey", bd=2,
                                 pady=2, highlightbackground="white", highlightthickness=0, wrap="none",
                                 insertbackground="white", relief="ridge", state="disabled")

        self.button_start = tkinter.Button(self, text="Generate Report", activebackground="grey", pady=5,
                                                      bg="black",
                                                      fg="white", highlightbackground="black", width=5, relief="ridge",
                                                      command=lambda: self.generate_report())

        self.rowconfigure(0, weight=1, uniform=1)
        self.rowconfigure(1, weight=4, uniform=1)
        self.rowconfigure(2, weight=1, uniform=1)
        self.rowconfigure(3, weight=62, uniform=1)
        self.rowconfigure(4, weight=1, uniform=1)
        self.columnconfigure(0, weight=1, uniform=1)
        self.columnconfigure(1, weight=30, uniform=1)
        self.columnconfigure(2, weight=1, uniform=1)

        self.button_start.grid(row=1, column=1, sticky="nsew")
        self.text.grid(row=3, column=1, sticky="nsew")

        self.get_engines()

        self.text.bind("<Button-2>", (lambda event: self.highlight_selectedline()))
        self.text.bind("<Double-Button-1>", (lambda event: self.show_content()))

    def highlight_selectedline(self):
        check_1 = 0
        check_2 = (self.text.get("current linestart", "current lineend") != "")

        if len(self.text.tag_names("current")) > 0:
            if self.text.tag_names("current")[0] == "sel":
                check_1 = 1

            if check_2 is True:
                if self.text.tag_configure(self.text.tag_names("current")[check_1])["background"][4] == "red":
                    self.text.tag_configure(self.text.tag_names("current")[check_1], background="black")
                else:
                    self.text.tag_configure(self.text.tag_names("current")[check_1], background="red")

    def get_engines(self):
        lst = [cls[6:] for cls in dir(sys.modules[__name__]) if cls.startswith("Method")]

        self.insert_files(lst)

    def insert_files(self, lst):
        self.clear_text()

        self.text.tag_configure("selected_line", background="black")

        self.text["state"] = "normal"
        for f in range(len(lst)):
            self.text.insert("end", lst[f] + "\n")
            self.text.see("end")
            self.text.tag_add(lst[f], str(float(f + 1)) + " linestart", str(float(f + 1)) + " lineend+1c")
        self.text["state"] = "disabled"

    def clear_text(self):
        self.text["state"] = "normal"
        self.text.delete('1.0', tkinter.END)
        self.text["state"] = "disabled"

    def show_content(self):
        check_1 = 0
        if self.text.tag_names("current")[0] == "sel":
            check_1 = 1
        key = self.text.tag_names("current")[check_1]

        readme = str_to_class("Method" + key).readme(self)

        popup = TextPopup(self, self.controller, key)
        popup.insert_text(readme)
        self.controller.master.wait_window(popup)

    def generate_report(self):
        files = []
        engines = []

        for tag in self.controller.file_list.text.tag_names():
            if self.controller.file_list.text.tag_configure(tag)["background"][4] == "red":
                files.append(tag)

        for tag in self.text.tag_names():
            if self.text.tag_configure(tag)["background"][4] == "red":
                engines.append(tag)

        if len(files) > 0 and len(engines) >= 0:
            self.progress_menu = ProgressMenu(self, self.controller, files, engines)
            self.controller.master.wait_window(self.progress_menu)


class TextPopup(tkinter.Toplevel):
    def __init__(self, parent, controller, key):
        tkinter.Toplevel.__init__(self, parent, bg="black", bd=5, relief="sunken")
        self.grid_propagate(0)
        self.winfo_toplevel().title(key)
        self.controller = controller

        self.rowconfigure(0, weight=1, uniform=1)
        self.columnconfigure(0, weight=1, uniform=1)

        self.selection = key
        self.parameters_input = {}

        self.container = tkinter.Frame(self, bg="black")
        self.container.pack(side="top", fill="both", expand=True)

        self.geometry("300x400+{0}+{1}".format(int(self.winfo_screenwidth() / 2) - 150, int(self.winfo_screenheight() / 2) - 200))

        self.container.rowconfigure(0, weight=1, uniform=1)
        self.container.columnconfigure(0, weight=1, uniform=1)

        self.container.text = tkinter.Text(self, bg="black", fg="white", font="Terminal, 12", selectbackground="grey",
                                           bd=2, pady=2, highlightbackground="white", highlightthickness=0, wrap="none",
                                           insertbackground="white", relief="ridge", state="disabled")

        self.container.text.grid(row=0, column=0, sticky="nsew", columnspan=3)

        self.container.text.focus_set()
        self.container.text.bind("<Return>", (lambda action: self.action_ok()))

    def action_ok(self):
        self.destroy()

    def read_file(self):
        path = os.path.dirname(
            os.path.realpath(__file__)) + "/files/" + self.selection.strip() + ".txt"
        txt = open(path, "r")
        file_config = txt.readline().split(",")
        txt.close()

        parameters = read_dict("CONFIG_PARAMETERS")

        for a in file_config:
            a = a.strip("\n")
            b = a.strip("[]").split(":")
            self.parameters_input[b[0]] = b[1]

        for x in parameters:
            if x in self.parameters_input:
                parameters[x] = self.parameters_input[x]

        self.clear_text()
        self.container.text["state"] = "normal"
        for p in parameters:
            self.container.text.insert("end", p + ": " + parameters[p] + "\n")
            self.container.text.see("end")
        self.container.text["state"] = "disabled"

    def insert_text(self, txt):
        self.clear_text()

        self.container.text["state"] = "normal"
        self.container.text.insert("end", txt + "\n")
        self.container.text.see("end")
        self.container.text["wrap"] = "word"
        self.container.text["state"] = "disabled"

    def clear_text(self):
        self.container.text["state"] = "normal"
        self.container.text.delete('1.0', tkinter.END)
        self.container.text["state"] = "disabled"


class ProgressMenu(tkinter.Toplevel):
    def __init__(self, parent, controller, files, engines):
        tkinter.Toplevel.__init__(self, parent, bg="black", bd=5, relief="sunken")
        self.grid_propagate(0)
        self.winfo_toplevel().title("Report Generation")
        self.controller = controller

        self.files = files
        self.engines = engines

        self.current_engine_index = 0
        self.current_engine = None

        self.base_directory = None

        self.geometry(
            "500x120+{0}+{1}".format(int(self.winfo_screenwidth() / 2) - 250, int(self.winfo_screenheight() / 2) - 50))

        self.rowconfigure(0, weight=1, uniform=1)
        self.rowconfigure(1, weight=1, uniform=1)
        self.rowconfigure(3, weight=1, uniform=1)
        self.rowconfigure(4, weight=1, uniform=1)
        self.columnconfigure(0, weight=1, uniform=1)
        self.columnconfigure(1, weight=1, uniform=1)
        self.columnconfigure(2, weight=1, uniform=1)
        self.columnconfigure(3, weight=1, uniform=1)
        self.columnconfigure(4, weight=1, uniform=1)

        self.button_cancel = tkinter.Button(self, text="CANCEL", activebackground="grey", pady=5,
                                                  bg="black",
                                                  fg="white", highlightbackground="black", width=5, relief="ridge",
                                                  command=lambda: self.action_cancel())

        self.loading_bar = LoadingBar(self, self)
        self.loading_progress = LoadingProgress(self, self)

        self.loading_progress.grid(row=0, column=0, sticky="nsew", columnspan=5, rowspan=2)
        self.loading_bar.grid(row=3, column=0, sticky="nsew", columnspan=5)
        self.button_cancel.grid(row=4, column=2, sticky="nsew")

        self.set_directory()

        self.loop()

        self.bind("<Return>", (lambda action: self.foo()))

    def action_cancel(self):
        self.unset_directory()
        self.destroy()

    def loop(self):
        self.current_engine = str_to_class("Method" + self.engines[self.current_engine_index])(self, self.files)

    def next_engine(self):
        if self.current_engine_index + 1 < len(self.engines):
            self.current_engine_index = self.current_engine_index + 1
            self.loop()
        else:
            self.report_complete()

    def set_directory(self):
        name = str(datetime.datetime.now()).split(".")[0]
        name = name.replace("-", ".", 2)
        name = name.replace(":", "-", 2)

        path = os.path.dirname(os.path.realpath(__file__)) + "/reports/" + name + "/"
        self.base_directory = path
        os.mkdir(path)

    def unset_directory(self):
        shutil.rmtree(self.base_directory)

    def report_complete(self):
        self.button_cancel.grid(row=4, column=3, sticky="nsew")
        self.button_cancel["text"] = "Delete"

        button_ok = tkinter.Button(self, text="Ok", activebackground="grey", pady=5,
                                            bg="black",
                                            fg="white", highlightbackground="black", width=5, relief="ridge",
                                            command=lambda: self.destroy())
        button_ok.grid(row=4, column=1, sticky="nsew")


class LoadingBar(tkinter.Frame):
    def __init__(self, parent, controller2):
        tkinter.Frame.__init__(self, parent, bg="black", bd=0, relief="ridge")
        self.grid_propagate(0)
        self.controller = controller2

        self.completion_rate = 0

        self.rowconfigure(0, weight=1, uniform=1)
        self.rowconfigure(1, weight=6, uniform=1)
        self.rowconfigure(2, weight=1, uniform=1)
        self.columnconfigure(0, weight=1, uniform=1)
        self.columnconfigure(1, weight=98, uniform=1)
        self.columnconfigure(2, weight=1, uniform=1)

        self.canvas = self.canvas = tkinter.Canvas(self, bg="white", bd=1, relief="ridge", highlightthickness=0)

        self.canvas.grid(row=1, column=1, sticky="nsew")

    def update_rate(self, new_rate):
        if new_rate >= 0:
            nr_discrete = math.floor(new_rate / 0.025)
            if nr_discrete - math.floor(self.completion_rate / 0.025) == 1:
                self.add_bar(math.floor(new_rate / 0.025))
            else:
                self.clear_canvas()
                for n in range(nr_discrete):
                    self.add_bar(n + 1)

            self.completion_rate = new_rate

    def clear_canvas(self):
        self.canvas.delete("all")

    def add_bar(self, n):
        r = math.floor(self.canvas.winfo_width()/40)
        self.canvas.create_rectangle(r*(n-1), 0, r*(n-1) + 10, self.canvas.winfo_height(), fill="green", outline="green")


class LoadingProgress(tkinter.Frame):
    def __init__(self, parent, controller2):
        tkinter.Frame.__init__(self, parent, bg="red", bd=0, relief="ridge")
        self.grid_propagate(0)
        self.controller = controller2

        self.total = len(self.controller.files) * len(self.controller.engines)
        self.completed = 0

        self.rowconfigure(0, weight=1, uniform=1)
        self.rowconfigure(1, weight=1, uniform=1)
        self.rowconfigure(2, weight=1, uniform=1)
        self.columnconfigure(0, weight=2, uniform=1)
        self.columnconfigure(1, weight=1, uniform=1)

        self.current_file = ParametersSubDisplay(self, self.controller, "Current_File:")
        self.current_method = ParametersSubDisplay(self, self.controller, "Current_Method:")
        self.progress = ParametersSubDisplay(self, self.controller, "Progress:")

        self.current_file.grid(row=0, column=0, sticky="nsew")
        self.current_method.grid(row=1, column=0, sticky="nsew")
        self.progress.grid(row=2, column=0, sticky="nsew")


class ParametersSubDisplay(tkinter.Frame):
    def __init__(self, parent, controller2, name1):
        tkinter.Frame.__init__(self, parent, bg="black", bd=0, relief="flat")
        self.grid_propagate(0)

        self.controller = controller2

        self.name = name1

        self.output = tkinter.StringVar()
        self.output.set("-")

        self.rowconfigure(0, weight=1, uniform=1)

        self.placeholder = tkinter.Label(self, bg="black", width=1)
        self.label = tkinter.Label(self, text=name1, font=("Terminal", 12, "bold"), bg="black", fg="white", bd=0, relief="ridge")
        self.output_label = tkinter.Label(self, textvariable=self.output, font=("Terminal", 12, "bold"), bg="black", fg="white", bd=0, relief="ridge", anchor="w")

        self.placeholder.grid(row=0, column=0, sticky="nsew", rowspan=1, columnspan=1)
        self.label.grid(row=0, column=1, sticky="w", rowspan=1, columnspan=1)
        self.output_label.grid(row=0, column=2, sticky="ew", rowspan=1, columnspan=1)


class MethodTimeInterval:
    def __init__(self, controller2, files):
        self.controller = controller2
        self.name = "TimeInterval"

        self.files = files
        self.current_file_index = 0
        self.current_file = self.files[self.current_file_index]

        self.completed = False

        self.update_progress()
        self.loop()

        # Engine-specific Attributes

    def engine_routine(self, data):
        pass

    def loop(self):
        if self.completed is True:
            self.shutdown()
        else:
            path = os.path.dirname(
                os.path.realpath(__file__)) + "/files/" + self.current_file + ".txt"
            txt = open(path, "r")
            import_data = txt.readlines()
            txt.close()

            self.engine_routine(import_data)

            if self.current_file_index + 1 < len(self.files):
                self.current_file_index = self.current_file_index + 1
                self.current_file = self.files[self.current_file_index]
                self.update_progress()
                self.loop()
            else:
                self.completed = True
                self.loop()

    def update_progress(self):
        self.controller.loading_bar.canvas.update()
        self.controller.loading_progress.current_file.output.set(self.current_file)
        self.controller.loading_progress.current_method.output.set(self.name)
        completed = str(self.controller.loading_progress.completed + self.current_file_index)
        total = str(self.controller.loading_progress.total)
        rate = str(round(float(completed) * 100 / float(total), 2))
        self.controller.loading_progress.progress.output.set(rate + "% | " + completed + " of " + total)
        self.controller.loading_bar.update_rate(float(rate))

    def readme(self):
        return "#######################################################################################################"

    def shutdown(self):
        self.current_file_index = 0
        self.current_file = self.files[self.current_file_index]
        self.controller.loading_progress.completed = self.controller.loading_progress.completed + len(self.files)
        self.update_progress()

        self.controller.next_engine()


class MethodPassivityCalculator:
    def __init__(self, controller2, files):
        self.controller = controller2
        self.name = "TimeInterval"

        self.files = files
        self.current_file_index = 0
        self.current_file = self.files[self.current_file_index]

        self.completed = False

        self.update_progress()
        self.loop()

        # Engine-specific Attributes

    def engine_routine(self, data):
        pass

    def loop(self):
        if self.completed is True:
            self.shutdown()
        else:
            path = os.path.dirname(
                os.path.realpath(__file__)) + "/files/" + self.current_file + ".txt"
            txt = open(path, "r")
            import_data = txt.readlines()
            txt.close()

            self.engine_routine(import_data)

            if self.current_file_index + 1 < len(self.files):
                self.current_file_index = self.current_file_index + 1
                self.current_file = self.files[self.current_file_index]
                self.update_progress()
                self.loop()
            else:
                self.completed = True
                self.loop()

    def update_progress(self):
        self.controller.loading_bar.canvas.update()
        self.controller.loading_progress.current_file.output.set(self.current_file)
        self.controller.loading_progress.current_method.output.set(self.name)
        completed = str(self.controller.loading_progress.completed + self.current_file_index)
        total = str(self.controller.loading_progress.total)
        rate = str(round(float(completed) * 100 / float(total), 2))
        self.controller.loading_progress.progress.output.set(rate + "% | " + completed + " of " + total)
        self.controller.loading_bar.update_rate(float(rate))

    def readme(self):
        return "#######################################################################################################"

    def shutdown(self):
        self.current_file_index = 0
        self.current_file = self.files[self.current_file_index]
        self.controller.loading_progress.completed = self.controller.loading_progress.completed + len(self.files)
        self.update_progress()

        self.controller.next_engine()


main()
