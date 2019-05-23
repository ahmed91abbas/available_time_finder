import tkinter as tk
from available_time_finder import Available_time_finder
import threading

class GUI:
    def __init__(self, url):
        self.stop_event = threading.Event()
        self.url = url
        self.interval = "3 seconds"
        self.number_results = 10
        self.finder = Available_time_finder(self.url, "Lund", self.number_results)
        self.create_gui()

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("WeDi")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)

        self.start_frame = tk.Frame(self.root)
        self.results_opt_frame = tk.Frame(self.root)
        self.buttons_frame = tk.Frame(self.root)
        self.status_frame = tk.Frame(self.root)
        self.list_frame = tk.Frame(self.root)

        pady = 10
        self.start_frame.pack(pady=pady)
        self.results_opt_frame.pack(pady=pady)
        self.buttons_frame.pack(pady=pady)
        self.status_frame.pack(pady=pady)
        self.list_frame.pack(pady=pady)

        tk.Label(self.start_frame, text="Select Area:").pack(side="left")
        def set_area(value):
            self.finder.area = value
        areas = ["Malmö", "Lund"]
        self.area_option = tk.StringVar()
        self.area_option.set(self.finder.area)
        self.area_options = tk.OptionMenu(self.start_frame, self.area_option, *areas, command=set_area)
        self.area_options.config(compound=tk.CENTER)
        self.area_options.pack(side="left")

        tk.Label(self.start_frame, text="Select refresh interval:").pack(side="left")
        def set_interval(value):
            self.interval = value
        intervals = ["3 seconds", "10 seconds", "30 seconds", "1 minute"]
        self.interval_option = tk.StringVar()
        self.interval_option.set(self.interval)
        self.interval_options = tk.OptionMenu(self.start_frame, self.interval_option, *intervals, command=set_interval)
        self.interval_options.config(compound=tk.CENTER)
        self.interval_options.pack(side="left")

        padx = 5
        box_width = 12
        tk.Label(self.results_opt_frame, text="Number of results:").pack(side="left", padx=padx)
        self.nbr_res_entry = tk.Entry(self.results_opt_frame, width=box_width)
        self.nbr_res_entry.insert(0, 10)
        self.nbr_res_entry.pack(side="left", padx=padx)

        padx = 20
        width = 10
        self.start_button = tk.Button(self.buttons_frame, text="Start", width=width, command=self.on_start)
        self.start_button.pack(side="left", padx=padx)
        self.stop_button = tk.Button(self.buttons_frame, text="Stop", width=width, command=self.on_stop)
        self.stop_button.pack(side="left", padx=padx)
        self.stop_button["state"] = "disabled"

        padx = 5
        width = 10
        tk.Label(self.status_frame, text="Status:").pack(side="left")
        self.status_label = tk.Label(self.status_frame, text="disconnected", width=width, bg="red")
        self.status_label.pack(side="left", padx=padx)

        tk.Label(self.status_frame, text="Next refresh in:").pack(side="left", padx=padx)

        wlist = 50
        hlist = 15
        scrollbar = tk.Scrollbar(self.list_frame)
        scrollbar.pack(side='right', fill=tk.Y)
        self.times_list = tk.Listbox(self.list_frame, width=wlist, height=hlist)
        self.times_list.pack()
        self.times_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.times_list.yview)

        self.root.mainloop()

    def on_start(self):
        self.start_button["state"] = "disabled"
        self.stop_button["state"] = "normal"
        try:
            self.finder.number_results = int(self.nbr_res_entry.get())
        except:
            self.nbr_res_entry.delete(0, "end")
            self.nbr_res_entry.insert(0, 10)
            self.finder.number_results = 10
        self.finder.connect()
        self.status_label.config(text="Connected", bg="green")
        self.get_results()

    def get_results(self):
        interval = self.interval_to_sec()
        times = self.finder.get_results()
        for time in times:
            self.times_list.insert(tk.END, time)
        #if(not self.stop_event.is_set()):
            # t = threading.Timer(self.interval, self.reset_and_run)
            # t.daemon = True
            # now = datetime.datetime.now()
            # next_run = now + datetime.timedelta(seconds=self.interval)
            # self.start_label['text'] = "Market: " + self.country_code + "\nNext iteration is scheduled on " + self.time_str(next_run)
            # t.start()

    def interval_to_sec(self):
        choice, unit = self.interval.split(" ")
        if unit == "minute" or unit == "minutes":
            return int(choice)*60
        else:
            return int(choice)

    def on_stop(self):
        self.stop_event.set()
        self.start_button["state"] = "normal"
        self.stop_button["state"] = "disabled"
        # try:
        #     self.finder.close_driver()
        # except:
        #     pass
        self.status_label.config(text="Disconnected", bg="red")

    def on_close(self):
        self.on_stop()
        self.root.destroy()

if __name__ == '__main__':
    url = "https://ventus.enalog.se/Booking/Booking/Index/skane"
    GUI(url)