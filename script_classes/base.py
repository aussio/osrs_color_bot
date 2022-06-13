from dataclasses import dataclass
import datetime
import time


@dataclass
class ScriptBase:

    duration: float
    num_runs: float
    loop_count: int = 0

    def run(self):
        """The entry point of any script.

        Runs the script in a while loop either for duration or num_runs.
        See the end of the while loop for what methods are called when.
        """

        start = time.time()

        start_datetime = datetime.datetime.fromtimestamp(start)
        if self.duration > 0:
            completed_time = start_datetime + datetime.timedelta(seconds=self.duration)
            print(
                f"Starting {self.__class__.__name__} at {start_datetime.strftime('%I:%M:%S%p')}. Will finish at: {completed_time.strftime('%I:%M:%S%p')}"
            )
        elif self.num_runs > 0:
            self.duration = float("inf")
            print(
                f"Starting {self.__class__.__name__} at {start_datetime.strftime('%I:%M:%S%p')}. Will run {self.num_runs} times."
            )
        else:
            raise Exception("Must specify either -d duration or -n num_runs.")

        elapsed = 0
        while elapsed < self.duration and self.loop_count < self.num_runs:
            elapsed = time.time() - start
            self.loop_count += 1
            if self.loop_count % 10 == 0:
                print(f"Repetition: {self.loop_count} Elapsed: {round(elapsed/60)}m")

            self.on_start()
            self.on_loop()
            self.on_sleep()
            self.on_stop()

    def on_start(self):
        pass

    def on_loop(self):
        raise NotImplementedError()

    def on_sleep(self):
        raise NotImplementedError()

    def on_stop(self):
        pass
