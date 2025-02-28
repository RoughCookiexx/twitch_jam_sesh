import time


class ObsTimer:

    def __init__(self, event, label, tk):
        self.label = label
        self.remaining_time = None
        self.running = False
        self.tk = tk
        self.event = event

    def update_timer(self):
        if self.remaining_time > 0 and self.running:
            self.remaining_time -= 1
            self.label.config(text=time.strftime('%M:%S', time.gmtime(self.remaining_time)))
            self.tk.after(1000, self.update_timer)
        else:
            self.reset_timer()
            self.event()

    def start_timer(self, minutes):
        self.remaining_time = minutes * 60
        self.running = True
        self.update_timer()

    def reset_timer(self):
        self.remaining_time = 0
        self.running = False
        self.label.config(text='00:00')

