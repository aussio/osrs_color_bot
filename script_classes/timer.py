from time import perf_counter


class timer:
    def __init__(self, print_label):
        self.label = print_label

    def __enter__(self):
        self.time = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.time = perf_counter() - self.time
        self.readout = f"{self.label}: Time: {self.time:.3f} seconds"
        print(self.readout)
