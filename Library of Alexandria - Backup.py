import tkinter
import cv2
import datetime
import PIL.Image
import PIL.ImageTk
import os
import playsound
import subprocess
import math
import random


def main():
    root = Alexandria()
    root.FileManager()
    root.mainloop()


def str_to_method(self, class_name):
    return getattr(VideoPlayer, class_name)(self)


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


class Alexandria(tkinter.Tk):
    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        self.grid_propagate(0)
        self.winfo_toplevel().title("Library of Alexandria")
        self.container = None

        self.side1 = None
        self.side2 = None

        self.selection = None
        self.vid_source = None

    def FileManager(self):
        self.container = tkinter.Frame(self, bg="black")
        self.container.pack(side="top", fill="both", expand=True)

        self.side1 = int(self.winfo_screenwidth() / 2)
        self.side2 = int(self.winfo_screenheight() / 2)

        self.geometry("{0}x{1}+{2}+{3}".format(self.side1, self.side2, int(self.side1 / 2),  int(self.side2 / 2)))

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=7)
        self.container.columnconfigure(1, weight=2)
        self.container.columnconfigure(2, weight=7)

        self.container.file_list = FileList(self.container, self.container)
        self.container.file_edit = FileEdit(self.container, self.container)
        self.container.button_set = ButtonSet(self.container, self.container)

        self.container.file_list.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=1)
        self.container.file_edit.grid(row=0, column=2, sticky="nsew", rowspan=2, columnspan=1)
        self.container.button_set.grid(row=0, column=1, sticky="nsew", rowspan=2, columnspan=1)

    def MainFrame(self):
        self.selection = self.container.file_list.selection
        self.vid_source = self.container.file_edit.parameters_input["FILE"]

        self.DeleteFrame()
        self.container = tkinter.Frame(self, bg="black")
        self.container.pack(side="top", fill="both", expand=True)

        self.side1 = int(self.winfo_screenwidth())
        self.side2 = int(self.winfo_screenheight())

        self.geometry("{0}x{1}+0+0".format(self.side1, self.side2))

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=6)
        self.container.columnconfigure(1, weight=2)

        self.container.video_player = VideoPlayer(self.container, self.container)
        self.container.tracker = Tracker(self.container, self.container)

        self.container.video_player.grid(row=0, column=0, sticky="nsew", rowspan=1, columnspan=1)
        self.container.tracker.grid(row=0, column=1, sticky="nsew", rowspan=1, columnspan=1)

        self.after(100, self.container.video_player.set_canvas())
        self.after(110, self.container.tracker.topographer.reset_canvas())
        self.after(115, self.container.tracker.tracker_reset())

    def DeleteFrame(self):
        self.container.destroy()

    def SaveData(self):
        tracker_data = self.container.tracker.text.get(1.0, tkinter.END).splitlines()

        path = os.path.dirname(
            os.path.realpath(__file__)) + "/files/" + self.selection.strip() + ".txt"

        txt = open(path, "r")
        base_data = txt.readline().strip("\n")
        txt.close()

        txt = open(path, "w")

        txt.write(base_data + "\n")
        txt.write("\n")
        for event in tracker_data:
            if len(event) > 0:
                if event[0] != "-":
                    txt.write(event + ",")
        txt.write("\n")

        txt.close()

        popup = LabelPopup(self, self.container, "File Succesfully Saved")
        self.container.master.wait_window(popup)


class FileList(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent, bg="black", bd=0, relief="ridge")
        self.grid_propagate(0)
        self.controller = controller

        self.selection = None
        self.loaded = False

        self.text = tkinter.Text(self, bg="black", fg="white", font="Terminal, 12", selectbackground="grey", bd=2,
                                 pady=2, highlightbackground="white", highlightthickness=0, wrap="none",
                                 insertbackground="white", relief="ridge", state="disabled")

        self.rowconfigure(0, weight=1, uniform=1)
        self.rowconfigure(1, weight=62, uniform=1)
        self.rowconfigure(2, weight=1, uniform=1)
        self.columnconfigure(0, weight=1, uniform=1)
        self.columnconfigure(1, weight=30, uniform=1)
        self.columnconfigure(2, weight=1, uniform=1)

        self.text.grid(row=1, column=1, sticky="nsew")

        self.get_files()
        self.text.bind("<Button-1>", (lambda event: self.highlight_selectedline()))

    def highlight_selectedline(self):
        check_1 = "selected_line" in self.text.tag_names("current")

        check_2 = (self.text.get("current linestart", "current lineend") != "")

        if check_2 is True:
            if (self.text.tag_configure("selected_line")["background"][4] == "red") and check_1 and check_2:
                self.text.tag_configure("selected_line", background="black")
            else:
                self.text.tag_configure("selected_line", background="red")
        else:
            self.text.tag_configure("selected_line", background="black")

        self.controller.file_edit.cancel()

        self.text.tag_remove("selected_line", 1.0, "end")
        self.text.tag_add("selected_line", "current linestart", "current lineend+1c")

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
        for f in lst:
            self.text.insert("end", f + "\n")
            self.text.see("end")
        self.text["state"] = "disabled"

    def clear_text(self):
        self.text["state"] = "normal"
        self.text.delete('1.0', tkinter.END)
        self.text["state"] = "disabled"

        return 1


class FileEdit(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent, bg="black", bd=0, relief="ridge")
        self.grid_propagate(0)
        self.controller = controller

        self.parameters_input = {}

        self.text = tkinter.Text(self, bg="black", fg="white", font="Terminal, 12", selectbackground="grey", bd=2,
                                 pady=2, highlightbackground="white", highlightthickness=0, wrap="none",
                                 insertbackground="white", relief="ridge", state="disabled")
        self.text.tag_configure("selected_line", background="black")

        self.rowconfigure(0, weight=1, uniform=1)
        self.rowconfigure(1, weight=62, uniform=1)
        self.rowconfigure(2, weight=1, uniform=1)
        self.columnconfigure(0, weight=1, uniform=1)
        self.columnconfigure(1, weight=30, uniform=1)
        self.columnconfigure(2, weight=1, uniform=1)

        self.text.grid(row=1, column=1, sticky="nsew")

    def read_file(self):
        path = os.path.dirname(
            os.path.realpath(__file__)) + "/files/" + self.controller.file_list.selection.strip() + ".txt"
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
        self.text["state"] = "normal"
        for p in parameters:
            self.text.insert("end", p + ": " + parameters[p] + "\n")
            self.text.see("end")
        self.text["state"] = "disabled"

        return 1

    def read_selection(self):
        text_list = self.controller.file_list.text

        if text_list.tag_configure("selected_line")["background"][4] == "red":
            self.controller.file_list.selection = text_list.get(str(text_list.tag_ranges("selected_line")[0]),
                                                                str(text_list.tag_ranges("selected_line")[1]))
            check = self.read_file()
            if check != 1:
                self.controller.file_list.selection = None

            return check

    def clear_text(self):
        self.text["state"] = "normal"
        self.text.delete('1.0', tkinter.END)
        self.text["state"] = "disabled"

        return 1

    def save(self):
        data = self.text.get(1.0, tkinter.END).splitlines()

        path = os.path.dirname(
            os.path.realpath(__file__)) + "/files/" + self.controller.file_list.selection.strip() + ".txt"

        txt = open(path, "r")
        file_data = txt.readlines()
        txt.close()

        new_config = ""
        skip_first = 0
        for n in data:
            d = n.split(":")
            if len(d) > 1:
                if skip_first != 0:
                    new_config = new_config + ","
                else:
                    skip_first = 1
                new_config = new_config + ("[" + d[0] + ":" + d[1].lstrip() + "]")

        new_config = new_config + "\n"

        file_data[0] = new_config

        txt = open(path, "w")

        for l in file_data:
            if len(l) > 0:
                txt.write(l)

        txt.close()

        self.edit_disabled()
        self.controller.file_list.get_files()

        return 1

    def edit_enable(self):
        self.text["state"] = "normal"

    def edit_disabled(self):
        self.text["state"] = "disabled"

    def cancel(self):
        self.controller.button_set.change_state(1)
        value = self.clear_text()
        return value

    def create_new(self):
        self.clear_text()
        self.edit_enable()

        parameters = read_dict("CONFIG_PARAMETERS")

        for p in parameters:
            self.text.insert("end", p + ": " + parameters[p] + "\n")
            self.text.see("end")

        self.edit_disabled()

        entry = EntryPopup(self, self.controller)
        self.controller.master.wait_window(entry)

        self.edit_enable()


class EntryPopup(tkinter.Toplevel):
    def __init__(self, parent, controller):
        tkinter.Toplevel.__init__(self, parent, bg="black", bd=5, relief="sunken")
        self.grid_propagate(0)
        self.winfo_toplevel().title("FILE NAME")
        self.controller = controller

        self.container = tkinter.Frame(self, bg="black")
        self.container.pack(side="top", fill="both", expand=True)

        self.geometry("200x50+{0}+{1}".format(int(self.winfo_screenwidth() / 2) - 100, int(self.winfo_screenheight() / 2) - 25))

        self.container.rowconfigure(0, weight=1, uniform=1)
        self.container.rowconfigure(1, weight=1, uniform=1)
        self.container.columnconfigure(0, weight=1, uniform=1)
        self.container.columnconfigure(1, weight=1, uniform=1)

        self.data = tkinter.StringVar()
        self.container.entry = tkinter.Entry(self.container, bg="white", bd=0, fg="black", font="Terminal, 12",
                                             selectbackground="grey", selectforeground="white", highlightthickness=0,
                                             insertbackground="black", textvariable=self.data)

        self.container.button_cancel = tkinter.Button(self.container, text="CANCEL", activebackground="grey", pady=5,
                                                      bg="black",
                                                      fg="white", highlightbackground="black", width=5, relief="ridge",
                                                      command=lambda: self.action_cancel())
        self.container.button_save = tkinter.Button(self.container, text="SAVE", activebackground="grey", pady=5,
                                                    bg="black",
                                                    fg="white", highlightbackground="black", width=5, relief="ridge",
                                                    command=lambda: self.action_save())

        self.container.entry.grid(row=0, column=0, sticky="nsew", columnspan=2)
        self.container.button_cancel.grid(row=1, column=0, sticky="nsew", columnspan=1)
        self.container.button_save.grid(row=1, column=1, sticky="nsew", columnspan=1)

    def action_cancel(self):
        self.destroy()
        self.controller.file_edit.cancel()

    def action_save(self):
        files_path = os.path.dirname(os.path.realpath(__file__)) + "/files"
        files = [f for f in os.listdir(files_path) if f.endswith('.txt')]

        in_use = False

        for f in files:
            if self.data.get() == f.rstrip(".txt"):
                in_use = True

        if in_use is False:
            self.destroy()
            self.controller.file_list.selection = self.data.get()


class ButtonSet(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent, bg="black", bd=0, relief="ridge")
        self.grid_propagate(0)
        self.controller = controller

        self.button1_text = tkinter.StringVar()
        self.button1_text.set("LOAD")
        self.button2_text = tkinter.StringVar()
        self.button2_text.set("CREATE NEW")
        self.button3_text = tkinter.StringVar()
        self.button3_text.set("START")

        self.state = 1
        self.change_state(self.state)

        self.button1 = tkinter.Button(self, textvariable=self.button1_text, activebackground="grey", pady=5, bg="black",
                                      fg="white", highlightbackground="black", width=5, relief="ridge",
                                      command=lambda: self.action_button1(self.button1_text.get()))
        self.button2 = tkinter.Button(self, textvariable=self.button2_text, activebackground="grey", pady=5, bg="black",
                                      fg="white", highlightbackground="black", width=5, relief="ridge",
                                      command=lambda: self.action_button2(self.button2_text.get()))
        self.button3 = tkinter.Button(self, textvariable=self.button3_text, activebackground="grey", pady=5, bg="black",
                                      fg="white", highlightbackground="black", width=5, relief="ridge",
                                      command=lambda: self.action_button3(self.button3_text.get()))

        self.rowconfigure(0, weight=1, uniform=1)
        self.rowconfigure(1, weight=30, uniform=1)
        self.rowconfigure(2, weight=2, uniform=1)
        self.rowconfigure(3, weight=30, uniform=1)
        self.rowconfigure(4, weight=2, uniform=1)
        self.rowconfigure(5, weight=30, uniform=1)
        self.rowconfigure(6, weight=1, uniform=1)
        self.columnconfigure(0, weight=1, uniform=1)
        self.columnconfigure(1, weight=30, uniform=1)
        self.columnconfigure(2, weight=1, uniform=1)

        self.button1.grid(row=1, column=1, sticky="nsew")
        self.button2.grid(row=3, column=1, sticky="nsew")
        self.button3.grid(row=5, column=1, sticky="nsew")

    def action_button1(self, action):
        if action == "LOAD":
            if self.controller.file_edit.read_selection() == 1:
                self.change_state(2)
        elif action == "CANCEL":
            if self.controller.file_edit.cancel() == 1:
                self.change_state(1)

    def action_button2(self, action):
        if action == "CREATE NEW":
            self.change_state(3)
            self.controller.file_edit.create_new()
        elif action == "EDIT":
            self.controller.file_edit.edit_enable()
            self.change_state(3)
        elif action == "SAVE":
            if self.controller.file_edit.save() == 1:
                self.change_state(2)

    def action_button3(self, action):
        if action == "START":
            if self.master.file_list.loaded is True:
                self.controller.master.MainFrame()

    def change_state(self, n):
        if n == 1:
            self.master.file_list.loaded = False
            self.button1_text.set("LOAD")
            self.button2_text.set("CREATE NEW")
            self.button3_text.set("START")
        elif n == 2:
            self.master.file_list.loaded = True
            self.button1_text.set("CANCEL")
            self.button2_text.set("EDIT")
            self.button3_text.set("START")
        elif n == 3:
            self.master.file_list.loaded = False
            self.button1_text.set("CANCEL")
            self.button2_text.set("SAVE")
            self.button3_text.set("START")


class VideoPlayer(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent, bg="black", bd=2, relief="ridge")
        self.grid_propagate(0)
        self.controller = controller

        self.rowconfigure(0, weight=44, uniform=0)
        self.rowconfigure(1, weight=1, uniform=0)
        self.rowconfigure(2, weight=3, uniform=0)
        self.columnconfigure(0, weight=1, uniform=0)

        self.video_source = os.path.dirname(
            os.path.realpath(__file__)) + "/videos/" + self.controller.master.vid_source + ".mp4"

        self.vid_class = MyVideoCapture(self.video_source, self.controller)
        self.fps = self.vid_class.vid.get(cv2.CAP_PROP_FPS)
        self.interval = 1000 / self.fps
        self.total_frames = int(self.vid_class.vid.get(cv2.CAP_PROP_FRAME_COUNT))
        self.preload = []
        self.time = datetime.datetime.now()

        self.playing_status = False
        self.discrete_mode = False
        self.rapid_edit = False
        self.rtn_mode = True

        self.reaction_time_normalizer = int(self.fps/5)

        self.active_frame = None
        self.scrollbar_position = None

        self.active_player = "BLUE"

        self.load_frames_engine_p1 = 0
        self.load_frames_engine_p2 = 0

        self.canvas = tkinter.Canvas(self, bg="black", bd=0)
        self.scrollbar = tkinter.Scrollbar(self, orient="horizontal", relief="flat", width=100, jump=1, command=lambda x, y: self.scrollbar_drag(x, y))
        self.button_set_player = ButtonSetPlayer(self, self.controller)

        self.canvas.grid(row=0, column=0, sticky="nsew", rowspan=1, columnspan=1)
        self.scrollbar.grid(row=1, column=0, sticky="nsew", rowspan=1, columnspan=1)
        self.button_set_player.grid(row=2, column=0, sticky="nsew", rowspan=1, columnspan=1)

        self.canvas.bind_all("<Key>", (lambda event: self.bind_key(event, "")))
        self.canvas.bind("<space>", (lambda event: self.key_mapper_space()))
        self.canvas.bind("<Left>", (lambda event: self.key_mapper_left()))
        self.canvas.bind("<Right>", (lambda event: self.key_mapper_right()))
        self.canvas.bind("<Up>", (lambda event: self.key_mapper_up()))
        self.canvas.bind("<Down>", (lambda event: self.key_mapper_down()))
        self.canvas.bind("<BackSpace>", (lambda event: self.key_mapper_backspace()))

    def time_update(self):
        self.time = datetime.datetime.now()

    def display_frame(self):
        # self.vid_class.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.vid_class.get_frame()
        if ret:
            photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=photo, anchor=tkinter.NW)
            self.canvas.image = photo
            self.active_frame = self.vid_class.vid.get(cv2.CAP_PROP_POS_FRAMES)
            self.update_scrollbar()
            self.canvas.focus_set()

            if self.active_frame == self.total_frames:
                self.playing_status = False

    def scrollbar_drag(self, x, y):
        frame = float(y)*self.total_frames
        self.display_frame_jump(frame)

    def display_frame_jump(self, frame):
        self.vid_class.vid.set(cv2.CAP_PROP_POS_FRAMES, frame)
        self.display_frame()
        self.controller.tracker.time_keeper_reset()

    def update_scrollbar(self):
        position = self.active_frame/self.total_frames
        if position < 0.01:
            position = 0.01
        offset = position - 0.01
        self.scrollbar.set(str(offset), str(position))

    def set_canvas(self):
        self.display_frame()

    def play_engine(self):
        if self.playing_status is True:
            self.display_frame()
            if self.discrete_mode is False:
                self.controller.tracker.time_keeper_engine(self.active_frame)
            else:
                self.controller.tracker.discrete_engine(self.active_frame)
            if self.controller.tracker.topographer.pairing_status is True:
                self.controller.tracker.topographer.display_canvas()

            self.after(int(self.interval), self.play_engine)

    def rapid_editor(self, key):
        ty_index = self.controller.tracker.text.tag_ranges("TY")
        event = self.controller.tracker.text.get(ty_index[0], ty_index[1])

        data = event.strip("\n").split(" | ")
        data[1] = data[1].split(".")

        if key == "q":
            # Body Shot
            data[1][1] = "B" + data[1][1][-1]

        if key == "w":
            # Head Shot
            data[1][1] = "H" + data[1][1][-1]

        if key == "e":
            # Punch
            data[1][1] = "S" + data[1][1][-1]

        if key == "a":
            # Right Leg
            data[1][2] = "R" + data[1][2][-1]

        if key == "s":
            # Left Leg
            data[1][2] = "L" + data[1][2][-1]

        if key == "z":
            # Front Leg
            data[1][2] = data[1][2][0] + "F"

        if key == "x":
            # Back Leg
            data[1][2] = data[1][2][0] + "B"

        if key.isdigit():
            # Technique
            data[1][1] = data[1][2][0] + key

        if key == "p":
            # Scoring Upgrade
            round_limit = False
            reset = False
            if data[1][1][0] == "H":
                score = 3
            elif data[1][1][0] == "B":
                score = 2
            elif data[1][1][0] == "S":
                score = 1
            elif data[1][1][0] == "P":
                round_limit = True
                score = 1
            else:
                score = -1

            if data[1][3] != "XXXX":
                score = score + 2

            for i in ["1", "4", "5"]:
                if i in data[1][3]:
                    reset = True

            point = "P" + str(abs(score))
            check = int(data[1][0])

            if score < 0:
                if check == 1:
                    check = 2
                elif check == 2:
                    check = 1

            if check == 1:
                point = point + "XX"
            elif check == 2:
                point = "XX" + point

            data[1][3] = point

            if round_limit is True:
                data[1][3] = "XXXX"
                if data[1][1][1] == "X":
                    data[1][1] = "PZ"
                else:
                    data[1][1] = "PX"

            if reset is True:
                data[1][3] = "XXXX"

        code = ""
        for i in data[1]:
            code = code + i + "."

        self.controller.tracker.delete_event()
        self.controller.tracker.discrete_input_tracker(code.strip("."), data[0].strip("[]"), data[2].strip("[]"), 0)
        self.controller.tracker.discrete_remap(int(data[0].strip("[]")) + 1)

    def key_mapper_space(self):
        self.bind_key("-", "space")

    def key_mapper_left(self):
        self.bind_key("-", "left")

    def key_mapper_right(self):
        self.bind_key("-", "right")

    def key_mapper_up(self):
        self.bind_key("-", "up")

    def key_mapper_down(self):
        self.bind_key("-", "down")

    def key_mapper_doubleclick(self):
        self.bind_key("-", "doubleclick")

    def key_mapper_backspace(self):
        self.bind_key("-", "backspace")

    def bind_key(self, obj, key):
        # print(obj)
        states = {0: "", 4: "control", 1: "shift", 2: "locked", 47: "locked", 96: "locked"}
        if obj != "-":
            if ((obj.char.isalpha() or obj.char.isdigit()) or obj.state != 0) and states[obj.state] != "locked":
                k = obj.char
                if obj.state != 0:
                    k = obj.keysym

                method_list = [f.split("_")[-1] for f in dir(VideoPlayer) if f.startswith('key_binder_')]

                if states[obj.state] + k in method_list:
                    str_to_method(self, "key_binder_" + states[obj.state] + k)

        else:
            str_to_method(self, "key_binder_" + key)

    def key_binder_space(self):
        if self.playing_status is False:
            self.playing_status = True
            self.play_engine()
        else:
            self.playing_status = False

    def key_binder_left(self):
        self.button_set_player.change_time(-1, 1)

    def key_binder_right(self):
        self.button_set_player.change_time(1, 1)

    def key_binder_up(self):
        if self.discrete_mode is True:
            ty_index = self.controller.tracker.text.tag_ranges("TY")
            indexer = str(float(str(ty_index[0])) - 1)
            if ty_index[0] == "1.0":
                indexer = ty_index[0]
            frame = None
            for tag in self.controller.tracker.text.tag_names(indexer):
                if tag.isdigit():
                    frame = int(tag)

            if frame is not None:
                self.display_frame_jump(frame)

    def key_binder_down(self):
        if self.discrete_mode is True:
            ty_index = self.controller.tracker.text.tag_ranges("TY")
            indexer = str(float(str(ty_index[0])) + 1)
            if ty_index[0] == str(float(self.controller.tracker.text.index('end').split('.')[0]) - 2):
                indexer = ty_index[0]
            frame = None
            for tag in self.controller.tracker.text.tag_names(indexer):
                if tag.isdigit():
                    frame = int(tag)

            if frame is not None:
                self.display_frame_jump(frame)

    def key_binder_doubleclick(self):
        if self.discrete_mode is True:
            frame = None

            for tag in self.controller.tracker.text.tag_names(tkinter.CURRENT):
                if tag.isdigit():
                    frame = int(tag)

            if frame is not None:
                self.display_frame_jump(frame)

    def key_binder_backspace(self):
        # Delete Event
        if self.discrete_mode is True:
            self.controller.tracker.delete_event()

    def key_binder_controls(self):
        # Save Data
        self.controller.master.SaveData()

    def key_binder_m(self):
        # Mode Changer
        self.controller.tracker.topographer.mode_button_action()

    def key_binder_shiftR(self):
        if self.discrete_mode is True:
            if self.rapid_edit is True:
                self.rapid_edit = False
                self.controller.tracker.qe_mode.output.set("N")
                self.controller.tracker.qe_mode.output_label["fg"] = "red"
            else:
                self.rapid_edit = True
                self.controller.tracker.qe_mode.output.set("Y")
                self.controller.tracker.qe_mode.output_label["fg"] = "green"

    def key_binder_shiftE(self):
        # Event Editor
        if self.discrete_mode is True:
            ty_index = self.controller.tracker.text.tag_ranges("TY")
            event = self.controller.tracker.text.get(ty_index[0], ty_index[1])
            popup = EventEditorPopup(self, self.controller, event)
            self.discrete_mode = False
            self.controller.master.wait_window(popup)

    def key_binder_v(self):
        if self.rapid_edit is False:
            code = "0.PX.XX.XXXX"
            if self.discrete_mode is True:
                self.controller.tracker.discrete_input_tracker(code, int(self.controller.video_player.active_frame) - self.reaction_time_normalizer, "GREEN", 1)
            else:
                self.controller.tracker.input_tracker(code, int(self.controller.video_player.active_frame) - self.reaction_time_normalizer, "GREEN", 1)

    def key_binder_c(self):
        if self.rapid_edit is False:
            a1 = "0"
            if self.active_player is "BLUE":
                a1 = "1"
            elif self.active_player is "RED":
                a1 = "2"
            code = a1 + ".FX.XX.XXXX"
            if self.discrete_mode is True:
                self.controller.tracker.discrete_input_tracker(code, int(self.controller.video_player.active_frame) - self.reaction_time_normalizer, "GREEN", 1)
            else:
                self.controller.tracker.input_tracker(code, int(self.controller.video_player.active_frame) - self.reaction_time_normalizer, "GREEN", 1)

    def key_binder_q(self):
        if self.rapid_edit is False:
            a1 = "0"
            if self.active_player is "BLUE":
                a1 = "1"
            elif self.active_player is "RED":
                a1 = "2"
            code = a1 + ".BX.XX.XXXX"

            if self.discrete_mode is True:
                self.controller.tracker.discrete_input_tracker(code, int(self.controller.video_player.active_frame) - self.reaction_time_normalizer, self.active_player, 1)
            else:
                self.controller.tracker.input_tracker(code, int(self.controller.video_player.active_frame) - self.reaction_time_normalizer, self.active_player, 1)

        elif self.rapid_edit is True:
            self.rapid_editor("q")

    def key_binder_w(self):
        if self.rapid_edit is False:
            a1 = "0"
            if self.active_player is "BLUE":
                a1 = "1"
            elif self.active_player is "RED":
                a1 = "2"
            code = a1 + ".HX.XX.XXXX"

            if self.discrete_mode is True:
                self.controller.tracker.discrete_input_tracker(code, int(self.controller.video_player.active_frame) - self.reaction_time_normalizer, self.active_player, 1)
            else:
                self.controller.tracker.input_tracker(code, int(self.controller.video_player.active_frame) - self.reaction_time_normalizer, self.active_player, 1)

        elif self.rapid_edit is True:
            self.rapid_editor("w")

    def key_binder_e(self):
        if self.rapid_edit is False:
            a1 = "0"
            if self.active_player is "BLUE":
                a1 = "1"
            elif self.active_player is "RED":
                a1 = "2"

            code = a1 + ".SX.XX.XXXX"

            if self.discrete_mode is True:
                self.controller.tracker.discrete_input_tracker(code, int(self.controller.video_player.active_frame) - self.reaction_time_normalizer, self.active_player, 1)
            else:
                self.controller.tracker.input_tracker(code, int(self.controller.video_player.active_frame) - self.reaction_time_normalizer, self.active_player, 1)

        elif self.rapid_edit is True:
            self.rapid_editor("e")

    def key_binder_a(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("a")

    def key_binder_s(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("s")

    def key_binder_z(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("z")

    def key_binder_x(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("x")

    def key_binder_p(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("p")

    def key_binder_1(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("1")

    def key_binder_2(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("2")

    def key_binder_3(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("3")

    def key_binder_4(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("4")

    def key_binder_5(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("5")

    def key_binder_6(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("6")

    def key_binder_7(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("7")

    def key_binder_8(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("8")

    def key_binder_9(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("9")

    def key_binder_0(self):
        if self.rapid_edit is False:
            pass
        elif self.rapid_edit is True:
            self.rapid_editor("0")


class ButtonSetPlayer(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent, bg="red", bd=0, relief="ridge")
        self.grid_propagate(0)
        self.controller = controller

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=10)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=10)
        self.columnconfigure(3, weight=10)
        self.columnconfigure(4, weight=4)
        self.columnconfigure(5, weight=4)
        self.columnconfigure(6, weight=4)

        # PLAY SET
        self.play_button = tkinter.Button(self, text="PLAY", activebackground="grey", bg="black", fg="white", highlightbackground="black", relief="ridge", command=lambda: self.play_button_action())
        self.pause_button = tkinter.Button(self, text="PAUSE", activebackground="grey", bg="black", fg="white", highlightbackground="black", relief="ridge", command=lambda: self.pause_button_action())
        self.rewind_3s_button = tkinter.Button(self, text="<< 2s", activebackground="grey", bg="black", fg="white", highlightbackground="black", relief="ridge", command=lambda: self.change_time(-1, 2))
        self.rewind_10s_button = tkinter.Button(self, text="<< 10s", activebackground="grey", bg="black", fg="white", highlightbackground="black", relief="ridge", command=lambda: self.change_time(-1, 10))
        self.forward_3s_button = tkinter.Button(self, text=">> 2s", activebackground="grey", bg="black", fg="white", highlightbackground="black", relief="ridge", command=lambda: self.change_time(1, 2))
        self.forward_10s_button = tkinter.Button(self, text=">> 10s", activebackground="grey", bg="black", fg="white", highlightbackground="black", relief="ridge", command=lambda: self.change_time(1, 10))
        self.save_button = tkinter.Button(self, text="SAVE", activebackground="grey", bg="black", fg="white", highlightbackground="black", relief="ridge", command=lambda: self.save_button_action())
        self.exit_button = tkinter.Button(self, text="EXIT", activebackground="grey", bg="black", fg="white", highlightbackground="black", relief="ridge", command=lambda: self.exit_button_action())

        self.play_button.grid(row=0, column=0, sticky="nsew", rowspan=1, columnspan=1)
        self.pause_button.grid(row=1, column=0, sticky="nsew", rowspan=1, columnspan=1)
        self.rewind_3s_button.grid(row=0, column=1, sticky="nsew", rowspan=1, columnspan=1)
        self.rewind_10s_button.grid(row=0, column=2, sticky="nsew", rowspan=1, columnspan=1)
        self.forward_3s_button.grid(row=1, column=1, sticky="nsew", rowspan=1, columnspan=1)
        self.forward_10s_button.grid(row=1, column=2, sticky="nsew", rowspan=1, columnspan=1)
        self.save_button.grid(row=0, column=6, sticky="nsew", rowspan=1, columnspan=1)
        self.exit_button.grid(row=1, column=6, sticky="nsew", rowspan=1, columnspan=1)

    def change_time(self, rf, s):
        frame = int(rf * (float(s) * self.master.fps) + self.master.active_frame)
        if frame < 1:
            frame = 1
        elif frame > self.master.total_frames:
            frame = self.master.total_frames - 1

        self.master.display_frame_jump(frame)

    def play_button_action(self):
        if self.master.playing_status is False:
            self.controller.video_player.key_binder_space()

    def pause_button_action(self):
        if self.master.playing_status is True:
            self.controller.video_player.key_binder_space()

    def exit_button_action(self):
        self.controller.master.DeleteFrame()
        self.controller.master.FileManager()

    def save_button_action(self):
        self.controller.master.SaveData()


class Tracker(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent, bg="black", bd=2, relief="ridge")
        self.grid_propagate(0)
        self.controller = controller

        self.tx_last_frame = None

        self.sound_effect = True
        self.sound_path = os.path.dirname(os.path.realpath(__file__)) + "/resources/"

        self.rowconfigure(0, weight=16, uniform=1)
        self.rowconfigure(1, weight=2, uniform=1)
        self.rowconfigure(2, weight=14, uniform=1)
        self.columnconfigure(0, weight=1, uniform=2)
        self.columnconfigure(1, weight=1, uniform=2)
        self.columnconfigure(2, weight=1, uniform=2)

        self.topographer = Topographer(self, self.controller)

        self.topographer.grid(row=0, column=0, sticky="nsew", rowspan=1, columnspan=3)

        self.text = tkinter.Text(self, bg="black", fg="white", font="Terminal, 12", selectbackground="grey", bd=0,
                                 pady=2, highlightbackground="white", highlightthickness=0, wrap="none",
                                 insertbackground="white", relief="ridge", state="normal")

        self.score_display = ParametersSubDisplay(self, self.controller, "SCORE:")

        self.qe_mode = ParametersSubDisplay(self, self.controller, "QE_MODE:")
        self.qe_mode.output.set("N")
        self.qe_mode.output_label["fg"] = "red"

        self.rtn_mode = ParametersSubDisplay(self, self.controller, "RTN:")
        self.rtn_mode.output.set(str(self.controller.video_player.reaction_time_normalizer))

        self.score_display.grid(row=1, column=0, sticky="nsew", rowspan=1, columnspan=1)
        self.qe_mode.grid(row=1, column=1, sticky="nsew", rowspan=1, columnspan=1)
        self.rtn_mode.grid(row=1, column=2, sticky="nsew", rowspan=1, columnspan=1)

        self.text.grid(row=2, column=0, sticky="nsew", rowspan=1, columnspan=3)

        self.text.bind("<Double-Button-1>", (lambda event: self.controller.video_player.key_mapper_doubleclick()))

    def input_tracker(self, code, frame, player, update):
        if int(frame) < 0:
            frame = "0"
        tx_index = self.text.tag_ranges("TX")

        if str(frame) in self.text.tag_names():
            frame = str(int(frame) + 1)

        self.text["state"] = "normal"
        self.text.insert(tx_index[0], "["+str(frame)+" | "+str(code)+" | "+player+"]\n")
        self.text.tag_add(str(frame), str(tx_index[0]) + " linestart", str(tx_index[0]) + " lineend+1c")
        self.text.tag_configure(str(frame), background=player)
        #self.text.see(str(float(str(tx_index[1])) + 11))
        self.margin_tracker(0)
        self.text["state"] = "disabled"

        if update is 1:
            self.text.update()

    def discrete_input_tracker(self, code, frame, player, update):
        if int(frame) < 0:
            frame = "0"
        ty_index = self.text.tag_ranges("TY")

        self.text["state"] = "normal"
        self.text.insert(ty_index[0], "[" + str(frame) + " | " + str(code) + " | " + player + "]\n")
        self.text.tag_add(str(frame), str(ty_index[0]) + " linestart", str(ty_index[0]) + " lineend+1c")
        self.text.tag_configure(str(frame), background=player)
        #self.text.see(str(float(str(ty_index[0])) + 11))
        self.margin_tracker(1)

        self.text["state"] = "disabled"

        if update is 1:
            self.text.update()

    def margin_tracker(self, mode):
        code = ""
        c = 1
        if mode == 0:
            code = "TX"
        elif mode == 1:
            code = "TY"
            c = 2
        index = self.text.tag_ranges(code)

        self.text.see(str(float(str(index[0])) + 10))
        self.text.see(str(float(str(index[0])) - 10 + c))

    def play_sound(self):
        pass
        #print("foo")
        #subprocess.call(["afplay", self.sound_path + str(self.controller.video_player.active_player) + ".wav"])
        #playsound.playsound(self.sound_path + str(self.controller.video_player.active_player) + ".wav")

    def delete_event(self):
        ty_index = self.text.tag_ranges("TY")

        self.text["state"] = "normal"
        self.text.tag_configure("TY", foreground="WHITE", lmargin1=0)

        for tag in self.text.tag_names(ty_index[0]):
            self.text.tag_delete(tag, ty_index[0], ty_index[1])

        self.text.delete(ty_index[0], ty_index[1])

        indexer = str(float(str(ty_index[0])) - 1)

        self.text.tag_add("TY", indexer + " linestart", indexer + " lineend+1c")
        self.text.tag_configure("TY", foreground="YELLOW", lmargin1=5)
        self.text["state"] = "disabled"
        self.text.update()

    def update_labels(self):
        pass

    def tracker_reset(self):
        self.time_keeper_reset()

        path = os.path.dirname(
            os.path.realpath(__file__)) + "/files/" + self.controller.master.selection.strip() + ".txt"

        txt = open(path, "r")
        import_data = txt.readlines()
        txt.close()

        if len(import_data) > 2:
            for event in import_data[2].strip("\n").split(","):
                if len(event) > 0:
                    data = event.split(" | ")
                    self.input_tracker(data[1].strip("[]"), data[0].strip("[]"), data[2].strip("[]"), 0)

            self.time_keeper_reset()

    def set_discrete_engine(self):
        tx_index = self.text.tag_ranges("TX")
        self.text["state"] = "normal"
        self.text.tag_remove("TX", 1.0, "end")
        self.text.delete(tx_index[0], tx_index[1])

        indexer = tx_index[0]
        if str(tx_index[0]) != "1.0":
            indexer = float(str(tx_index[0])) - 1

        self.text.tag_add("TY", str(indexer) + " linestart", str(indexer) + " lineend+1c")
        self.text.tag_configure("TY", foreground="YELLOW", lmargin1=5)
        self.text["state"] = "disabled"

    def unset_discrete_engine(self):
        self.text.tag_configure("TY", foreground="WHITE", lmargin1=0)
        self.text.tag_remove("TY", 1.0, "end")
        self.controller.video_player.playing_status = False
        self.time_keeper_remap(1)

    def discrete_engine(self, frame):
        ty_index = self.text.tag_ranges("TY")
        check = 0

        if int(frame) - self.tx_last_frame == 1:
            if len(self.text.tag_names(ty_index[1])) != 0:
                if "sel" in self.text.tag_names(ty_index[1]):
                    check = 1
                if int(self.text.tag_names(ty_index[1])[0 + check]) < frame:
                    self.text["state"] = "normal"
                    self.text.tag_configure("TY", foreground="WHITE", lmargin1=0)
                    self.text.tag_remove("TY", 1.0, "end")

                    self.text.tag_add("TY", str(ty_index[1]) + " linestart", str(ty_index[1]) + " lineend+1c")
                    self.text.tag_configure("TY",  foreground="YELLOW", lmargin1=5)
                    # self.text.see(str(float(str(ty_index[1])) + 10))
                    self.margin_tracker(1)
                    self.text["state"] = "disabled"
                    self.text.update()

                    if self.sound_effect is True:
                        self.play_sound()

                self.tx_last_frame = int(frame)
            self.tx_last_frame = int(frame)
        else:
            self.engine_jumper(frame)

    def time_keeper_reset(self):
        self.engine_jumper(self.controller.video_player.active_frame)
        self.tx_last_frame = int(self.controller.video_player.active_frame)

    def time_keeper_engine(self, frame):
        tx_index = self.text.tag_ranges("TX")
        check = 0

        if int(frame) - self.tx_last_frame == 1:
            if len(self.text.tag_names(tx_index[1])) != 0:
                if "sel" in self.text.tag_names(tx_index[1]):
                    check = 1
                if int(self.text.tag_names(tx_index[1])[0 + check]) < frame:

                    self.text["state"] = "normal"
                    self.text.tag_remove("TX", 1.0, "end")
                    self.text.delete(tx_index[0], tx_index[1])
                    self.text.insert(tx_index[1], "-------------------------------------------------------\n")
                    self.text.tag_add("TX", str(tx_index[1]) + " linestart", str(tx_index[1]) + " lineend+1c")
                    self.text.tag_configure("TX", background="yellow", foreground="black")
                    # self.text.see(str(float(str(tx_index[1])) + 10))
                    self.margin_tracker(0)
                    self.text["state"] = "disabled"
                    self.text.update()

                    if self.sound_effect is True:
                        self.after(5,self.play_sound())

                self.tx_last_frame = int(frame)
            self.tx_last_frame = int(frame)
        else:
            self.engine_jumper(frame)

    def engine_jumper(self, frame):
        check_value = False

        for i in range(int(self.text.index('end').split('.')[0]) + 1):
            if check_value is False:
                indexer = str(i + 1) + ".0"

                for tag in self.text.tag_names(indexer):
                    if tag.isdigit():
                        if int(tag) >= int(frame):
                            check_value = True

                            indexer = str(i) + ".0"

                            if self.controller.video_player.discrete_mode is False:

                                tx_index = self.text.tag_ranges("TX")
                                self.text["state"] = "normal"
                                if len(tx_index) > 0:
                                    self.text.tag_remove("TX", 1.0, "end")
                                    self.text.delete(tx_index[0], tx_index[1])

                                self.text.insert(indexer, "-------------------------------------------------------\n")
                                self.text.tag_add("TX", indexer + " linestart", indexer + " lineend+1c")
                                self.text.tag_configure("TX", background="yellow", foreground="black")
                                #self.text.see(str(float(indexer) + 10))
                                self.margin_tracker(0)
                                self.text["state"] = "disabled"
                                self.text.update()
                                if self.sound_effect is True:
                                    self.play_sound()

                                self.tx_last_frame = int(frame)

                            else:
                                ty_index = self.text.tag_ranges("TY")

                                self.text["state"] = "normal"
                                if len(ty_index) > 0:
                                    self.text.tag_configure("TY", foreground="WHITE", lmargin1=0)
                                    self.text.tag_remove("TY", 1.0, "end")

                                self.text.tag_add("TY", indexer + " linestart", indexer + " lineend+1c")
                                self.text.tag_configure("TY", foreground="YELLOW", lmargin1=5)
                                #self.text.see(str(float(indexer) + 10))
                                self.margin_tracker(1)
                                self.text["state"] = "disabled"
                                self.text.update()
                                if self.sound_effect is True:
                                    self.play_sound()

                                self.tx_last_frame = int(frame)

        if check_value is False:
            if self.controller.video_player.discrete_mode is False:
                tx_index = self.text.tag_ranges("TX")

                if len(tx_index) > 0:
                    self.text["state"] = "normal"
                    self.text.tag_remove("TX", 1.0, "end")
                    self.text.delete(tx_index[0], tx_index[1])

                indexer = str(float(self.text.index('end').split('.')[0]) - 1)
                self.text["state"] = "normal"
                self.text.insert(indexer, "-------------------------------------------------------\n")
                self.text.tag_add("TX", indexer + " linestart", indexer + " lineend+1c")
                self.text.tag_configure("TX", background="yellow", foreground="black")
                #self.text.see(indexer)
                self.margin_tracker(0)
                self.text["state"] = "disabled"
                self.text.update()
                if self.sound_effect is True:
                    self.play_sound()

                self.tx_last_frame = int(frame)

            else:
                ty_index = self.text.tag_ranges("TY")

                if len(ty_index) > 0:
                    self.text["state"] = "normal"
                    self.text.tag_configure("TY", foreground="WHITE", lmargin1=0)
                    self.text.tag_remove("TY", 1.0, "end")

                indexer = str(float(self.text.index('end').split('.')[0]) - 2)
                self.text.tag_add("TY", indexer + " linestart", indexer + " lineend+1c")
                self.text.tag_configure("TY", foreground="YELLOW", lmargin1=5)
                #self.text.see(indexer)
                self.margin_tracker(1)
                self.text["state"] = "disabled"
                self.text.update()
                if self.sound_effect is True:
                    self.play_sound()

                self.tx_last_frame = int(frame)

    def tracker_data_normalization(self, tracker_data):
        frames = {""}
        for i in range(len(tracker_data) - 1):
            frames.add(int(tracker_data[i].split(" | ")[0].strip("[]")))

        if len(tracker_data) == len(frames):
            return tracker_data
        else:
            for i in range(len(tracker_data) - 2):
                if int(tracker_data[i].split(" | ")[0].strip("[]")) == int(tracker_data[i + 1].split(" | ")[0].strip("[]")):
                    data = tracker_data[i + 1].split(" | ")
                    f = int(data[0].strip("[]")) + 1
                    tracker_data[i + 1] = "[" + str(f) + " | " + data[1] + " | " + data[2] + "]"

            return tracker_data

    def time_keeper_remap(self, mode):
        tracker_data = self.text.get(1.0, tkinter.END).splitlines()

        tracker_data = self.tracker_data_normalization(tracker_data)

        self.text["state"] = "normal"
        self.text.delete('1.0', tkinter.END)
        for tag in self.text.tag_names():
            self.text.tag_delete(tag)
        self.text["state"] = "disabled"

        self.time_keeper_reset()

        score = [0, 0]

        while len(tracker_data) > mode:
            min_val = None
            min_val_tag = None
            for event in tracker_data:
                if len(event) > 0:
                    if event[0] != "-":
                        val = int(event.split(" | ")[0].strip("[]"))
                        if min_val is None:
                            min_val = val
                            min_val_tag = event
                        else:
                            if val < min_val:
                                min_val = val
                                min_val_tag = event

            data = min_val_tag.split(" | ")
            self.input_tracker(data[1].strip("[]"), data[0].strip("[]"), data[2].strip("[]"), 0)

            score_code = data[1].split(".")[3]
            if score_code != "XXXX":
                if score_code[0] == "P":
                    score[0] = score[0] + int(score_code[1])
                elif score_code[0] == "N":
                    score[0] = score[0] - int(score_code[1])
                if score_code[2] == "P":
                    score[1] = score[1] + int(score_code[3])
                elif score_code[2] == "N":
                    score[1] = score[1] - int(score_code[3])

            self.score_display.output.set(str(score[0]) + " / " + str(score[1]))

            tracker_data.remove(min_val_tag)
        if score[0] > score[1]:
            self.score_display.output_label["fg"] = "blue"
        elif score[0] < score[1]:
            self.score_display.output_label["fg"] = "red"
        else:
            self.score_display.output_label["fg"] = "green"

        self.time_keeper_reset()

    def discrete_remap(self, frame):
        tracker_data = self.text.get(1.0, tkinter.END).splitlines()

        self.text["state"] = "normal"
        self.text.delete('1.0', tkinter.END)
        for tag in self.text.tag_names():
            self.text.tag_delete(tag)
        self.text["state"] = "disabled"

        self.time_keeper_reset()

        while len(tracker_data) > 1:
            min_val = None
            min_val_tag = None
            for event in tracker_data:
                if len(event) > 0:
                    val = int(event.split(" | ")[0].strip("[]"))
                    if min_val is None:
                        min_val = val
                        min_val_tag = event
                    else:
                        if val < min_val:
                            min_val = val
                            min_val_tag = event

            data = min_val_tag.split(" | ")

            self.discrete_input_tracker(data[1].strip("[]"), data[0].strip("[]"), data[2].strip("[]"), 0)

            tracker_data.remove(min_val_tag)

        ty_index = self.text.tag_ranges("TY")

        if len(ty_index) > 0:
            self.text["state"] = "normal"
            self.text.tag_configure("TY", foreground="WHITE", lmargin1=0)
            self.text.tag_remove("TY", 1.0, "end")

        indexer = str(float(self.text.index('end').split('.')[0]) - 2)
        self.text.tag_add("TY", indexer + " linestart", indexer + " lineend+1c")
        self.text.tag_configure("TY", foreground="YELLOW", lmargin1=5)
        #self.text.see(indexer)
        self.margin_tracker(1)
        self.text["state"] = "disabled"
        self.text.update()

        self.engine_jumper(frame)


class EventEditorPopup(tkinter.Toplevel):
    def __init__(self, parent, controller, event):
        tkinter.Toplevel.__init__(self, parent, bg="black", bd=5, relief="sunken")
        self.grid_propagate(0)
        self.winfo_toplevel().title("EVENT EDITOR")
        self.controller = controller

        self.container = tkinter.Frame(self, bg="black")
        self.container.pack(side="top", fill="both", expand=True)

        self.geometry("300x50+{0}+{1}".format(int(self.winfo_screenwidth() / 2) - 100, int(self.winfo_screenheight() / 2) - 25))

        self.container.rowconfigure(0, weight=1, uniform=1)
        self.container.rowconfigure(1, weight=1, uniform=1)
        self.container.columnconfigure(0, weight=1, uniform=1)
        self.container.columnconfigure(1, weight=1, uniform=1)

        self.data = tkinter.StringVar()
        self.data.set(event)
        self.color = self.data.get().strip("\n").split(" | ")[2].strip("[]")
        self.container.entry = tkinter.Entry(self.container, bg=self.color, bd=0, fg="black", font=("Terminal", 12, "bold"),
                                             selectbackground="grey", selectforeground="white", highlightthickness=0,
                                             insertbackground="black", textvariable=self.data)

        self.container.button_cancel = tkinter.Button(self.container, text="CANCEL", activebackground="grey", pady=5,
                                                      bg="black",
                                                      fg="white", highlightbackground="black", width=5, relief="ridge",
                                                      command=lambda: self.action_cancel())
        self.container.button_save = tkinter.Button(self.container, text="SAVE", activebackground="grey", pady=5,
                                                    bg="black",
                                                    fg="white", highlightbackground="black", width=5, relief="ridge",
                                                    command=lambda: self.action_save())

        self.container.entry.grid(row=0, column=0, sticky="nsew", columnspan=2)
        self.container.button_cancel.grid(row=1, column=0, sticky="nsew", columnspan=1)
        self.container.button_save.grid(row=1, column=1, sticky="nsew", columnspan=1)

        self.container.entry.focus_set()
        self.container.entry.bind("<Return>", (lambda action: self.action_save()))
        self.container.entry.bind("<Escape>", (lambda action: self.action_cancel()))

    def action_cancel(self):
        self.destroy()
        self.controller.video_player.discrete_mode = True

    def action_save(self):
        self.destroy()
        self.controller.video_player.discrete_mode = True
        self.controller.video_player.canvas.focus_set()

        self.controller.tracker.delete_event()
        event = self.data.get().strip("\n").split(" | ")

        self.controller.tracker.discrete_input_tracker(event[1].strip("[]"), event[0].strip("[]"), event[2].strip("[]"), 0)
        self.controller.tracker.discrete_remap(int(event[0].strip("[]")) + 1)


class ParametersSubDisplay(tkinter.Frame):
    def __init__(self, parent, controller, name1):
        tkinter.Frame.__init__(self, parent, bg="black", bd=0, relief="flat")
        self.grid_propagate(1)

        self.controller = controller

        self.name = name1

        self.output = tkinter.StringVar()
        self.output.set("-")

        self.rowconfigure(0, weight=1, uniform=1)

        self.placeholder = tkinter.Label(self, bg="black", width=1)
        self.label = tkinter.Label(self, text=name1, font=("Terminal", 12, "bold"), bg="black", fg="white", bd=0, relief="ridge")
        self.output_label = tkinter.Label(self, textvariable=self.output, font=("Terminal", 12, "bold"), bg="black", fg="white", bd=0, relief="ridge")

        self.placeholder.grid(row=0, column=0, sticky="nsew", rowspan=1, columnspan=1)
        self.label.grid(row=0, column=1, sticky="w", rowspan=1, columnspan=1)
        self.output_label.grid(row=0, column=2, sticky="ew", rowspan=1, columnspan=1)


class LabelPopup(tkinter.Toplevel):
    def __init__(self, parent, controller, key):
        tkinter.Toplevel.__init__(self, parent, bg="black", bd=5, relief="sunken")
        self.grid_propagate(0)
        self.winfo_toplevel().title("")
        self.controller = controller

        self.container = tkinter.Frame(self, bg="black")
        self.container.pack(side="top", fill="both", expand=True)

        self.geometry("200x50+{0}+{1}".format(int(self.winfo_screenwidth() / 2) - 100, int(self.winfo_screenheight() / 2) - 25))

        self.container.rowconfigure(0, weight=1, uniform=1)
        self.container.rowconfigure(1, weight=1, uniform=1)
        self.container.columnconfigure(0, weight=1, uniform=1)
        self.container.columnconfigure(1, weight=1, uniform=1)
        self.container.columnconfigure(2, weight=1, uniform=1)

        self.data = tkinter.StringVar()
        self.data.set(key)
        self.container.label = tkinter.Label(self.container, bg="white", bd=0, fg="black", font=("Terminal", 12, "bold"), textvariable=self.data)

        self.container.button_ok = tkinter.Button(self.container, text="OK", activebackground="grey", pady=5,
                                                      bg="black",
                                                      fg="white", highlightbackground="black", width=5, relief="ridge",
                                                      command=lambda: self.action_ok())

        self.container.label.grid(row=0, column=0, sticky="nsew", columnspan=3)
        self.container.button_ok.grid(row=1, column=1, sticky="nsew", columnspan=1)

        self.container.label.focus_set()
        self.container.label.bind("<Return>", (lambda action: self.action_ok()))

    def action_ok(self):
        self.destroy()


class Topographer(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent, bg="blue", bd=2, relief="ridge")
        self.grid_propagate(0)
        self.controller = controller

        self.pairing_status = False
        self.displayed_frame = 0

        self.active_topography = 0

        self.topography = [[[0, 0]], [[0, 0]]]

        self.rowconfigure(0, weight=43, uniform=0)
        self.rowconfigure(1, weight=2, uniform=0)
        self.rowconfigure(2, weight=3, uniform=0)
        self.columnconfigure(0, weight=1, uniform=0)
        self.columnconfigure(1, weight=1, uniform=0)
        self.columnconfigure(2, weight=1, uniform=0)

        self.canvas = tkinter.Canvas(self, bg="blue", bd=0)
        self.scrollbar = tkinter.Scrollbar(self, orient="horizontal", relief="flat", width=100, jump=1,
                                           command=lambda x, y: print("foo"))
        self.pairing_button = tkinter.Button(self, text="NOT PAIRED", activebackground="grey", bg="black", fg="white",
                                          highlightbackground="black", relief="ridge",
                                          command=lambda: self.pairing_button_action())
        self.mode_button = tkinter.Button(self, text="CONTINUOUS", activebackground="grey", bg="black", fg="white",
                                             highlightbackground="black", relief="ridge",
                                             command=lambda: self.mode_button_action())
        self.player = tkinter.StringVar()
        self.player.set(self.controller.video_player.active_player)
        self.active_player_button = tkinter.Button(self, textvariable=self.player, activebackground="grey", bg="black", fg="white",
                                          highlightbackground="black", relief="ridge",
                                          command=lambda: self.active_player_button_action())

        self.canvas.grid(row=0, column=0, sticky="nsew", rowspan=1, columnspan=3)
        self.scrollbar.grid(row=1, column=0, sticky="nsew", rowspan=1, columnspan=3)
        self.pairing_button.grid(row=2, column=0, sticky="nsew", rowspan=1, columnspan=1)
        self.mode_button.grid(row=2, column=1, sticky="nsew", rowspan=1, columnspan=1)
        self.active_player_button.grid(row=2, column=2, sticky="nsew", rowspan=1, columnspan=1)

    def reset_canvas(self):
        if self.canvas.winfo_width() < self.canvas.winfo_height():
            base_dim = int(self.canvas.winfo_width()*0.9)/3
            base_dim_w = 0
            base_dim_h = int((self.canvas.winfo_height() - self.canvas.winfo_width())/1.5)
        else:
            base_dim = int(self.canvas.winfo_height()*0.9)/3
            base_dim_w = int((self.canvas.winfo_width() - self.canvas.winfo_height())/1.5)
            base_dim_h = 0

        self.canvas.create_rectangle(0, 0, self.canvas.winfo_width()/2, self.canvas.winfo_height(), fill="red")

        a = 3/(2 + math.sqrt(2))
        self.canvas.create_polygon((a + 0.15) * base_dim + base_dim_w, (0 + 0.15) * base_dim + base_dim_h,
                                   (a * (1 + math.sqrt(2)) + 0.15) * base_dim + base_dim_w,
                                   (0 + 0.15) * base_dim + base_dim_h,
                                   (a * (2 + math.sqrt(2)) + 0.15) * base_dim + base_dim_w,
                                   (a + 0.15) * base_dim + base_dim_h,
                                   (a * (2 + math.sqrt(2)) + 0.15) * base_dim + base_dim_w,
                                   (a * (1 + math.sqrt(2)) + 0.15) * base_dim + base_dim_h,
                                   (a * (1 + math.sqrt(2)) + 0.15) * base_dim + base_dim_w,
                                   (a * (2 + math.sqrt(2)) + 0.15) * base_dim + base_dim_h,
                                   (a + 0.15) * base_dim + base_dim_w,
                                   (a * (2 + math.sqrt(2)) + 0.15) * base_dim + base_dim_h,
                                   (0 + 0.15) * base_dim + base_dim_w,
                                   (a * (1 + math.sqrt(2)) + 0.15) * base_dim + base_dim_h,
                                   (0 + 0.15) * base_dim + base_dim_w, (a + 0.15) * base_dim + base_dim_h,
                                   fill="white", outline="black", width=4)

    def display_canvas(self):
        frame = self.controller.video_player.active_frame
        print()
        if self.displayed_frame is not None:
            print("foo")
            if frame - self.displayed_frame >= int(self.controller.video_player.fps/2):
                print(frame)
                length = len(self.topography[self.active_topography])
                if int(frame/self.controller.video_player.fps/2) > length:
                    print("shit")
                    coord = self.topography[self.active_topography][length-1]
                    for n in range(int(frame/self.controller.video_player.fps/2) - length):
                        self.topography[self.active_topography].append(coord)
                print(self.topography[self.active_topography][length])

    def pairing_button_action(self):
        if self.pairing_status is False:
            # self.pairing_status = True
            self.pairing_button["text"] = "PAIRED"
            self.master.input_tracker(datetime.datetime.now(), int(self.controller.video_player.active_frame), self.controller.video_player.active_player, 1)
        else:
            # self.pairing_status = False
            self.pairing_button["text"] = "NOT PAIRED"
            self.master.input_tracker(datetime.datetime.now(), int(self.controller.video_player.active_frame), "RED", 1)

    def mode_button_action(self):
        if self.controller.video_player.discrete_mode is False:
            self.controller.video_player.discrete_mode = True
            self.mode_button["text"] = "DISCRETE"
            self.controller.tracker.set_discrete_engine()
        else:
            self.controller.video_player.discrete_mode = False
            self.controller.video_player.rapid_edit = False
            self.controller.tracker.qe_mode.output.set("N")
            self.controller.tracker.qe_mode.output_label["fg"] = "red"
            self.mode_button["text"] = "CONTINUOUS"
            self.controller.tracker.unset_discrete_engine()


    def active_player_button_action(self):
        if self.controller.video_player.active_player is "BLUE":
            self.controller.video_player.active_player = "RED"
            self.player.set(self.controller.video_player.active_player)
        else:
            self.controller.video_player.active_player = "BLUE"
            self.player.set(self.controller.video_player.active_player)


class MyVideoCapture:
    def __init__(self, video_source, controller):
        self.vid = cv2.VideoCapture(video_source)

        self.controller = controller

        if not self.vid.isOpened():
            # Show Warning in Canvas
            raise ValueError("Unable to open video source", video_source)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                self.controller.video_player.canvas.update()
                frame = cv2.resize(frame, (self.controller.video_player.canvas.winfo_width(), self.controller.video_player.canvas.winfo_height()))

                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return None
        else:
            return None


main()
