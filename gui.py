import tkinter as tk
from available_time_finder import Available_time_finder

class GUI:
    def __init__(self, url):
        self.url = url
        self.area = "Lund"
        self.interval = "3 seconds"
        self.number_results = 10
        self.finder = Available_time_finder(self.url, self.area, self.number_results)
        self.create_gui()

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("WeDi")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)

        self.start_frame = tk.Frame(self.root)
        self.buttons_frame = tk.Frame(self.root)
        self.list_frame = tk.Frame(self.root)

        pady = 10
        self.start_frame.pack(pady=pady)
        self.buttons_frame.pack(pady=pady)
        self.list_frame.pack(pady=pady)

        tk.Label(self.start_frame, text="Select Area:").pack(side="left")
        def set_area(value):
            self.area = value
        areas = ["Malmö", "Lund"]
        self.area_option = tk.StringVar()
        self.area_option.set(self.area)
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

        padx = 20
        self.start_button = tk.Button(self.buttons_frame, text="Start", command=self.on_start)
        self.start_button.pack(side="left", padx=padx)
        self.stop_button = tk.Button(self.buttons_frame, text="Stop", command=self.on_stop)
        self.stop_button.pack(side="left", padx=padx)

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
        self.finder.connect()
        times = self.finder.get_results()
        for time in times:
            self.times_list.insert(tk.END, time)

    def on_stop(self):
        try:
            self.finder.close_driver()
        except:
            pass

    def on_close(self):
        self.on_stop()
        self.root.destroy()

if __name__ == '__main__':
    url = "https://ventus.enalog.se/Booking/Booking/Index/skane"
    GUI(url)