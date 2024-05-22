import threading
import time
from typing import Callable, Any

class TaskQueue:
    def __init__(self, task_delay: int):
        """
        Creates a task queue with a specified delay between tasks.
        If a task is added to the queue, it will be executed after the specified delay has passed since the last task started.
        Only one task is executed at a time, in the order they were added.
        """
        self.task_delay = task_delay
        self.last_task_time = time.time() - self.task_delay  # Initialize to enable immediate first action
        self.lock = threading.Lock()
        self.queue = []
        self.event = threading.Event()
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()

    def _get_initial_wait(self):
        time_since_last_task = time.time() - self.last_task_time
        time_to_wait = max(self.task_delay - time_since_last_task, 0)
        return time_to_wait
    
    def get_estimated_wait(self, ahead: int = 0):
        """
        Returns the estimated time in seconds until the last task in the queue will be executed.
        If `ahead` is specified, it returns the estimated time as if there were `ahead` more tasks in the queue.
        """
        with self.lock:
            inital_wait = self._get_initial_wait()
            consequent_wait = max(self.task_delay * (len(self.queue) - 1 + ahead), 0)
            return inital_wait + consequent_wait

    def add(self, task: Callable, *args, **kwargs):
        """
        Adds a task along with its arguments to the task queue.
        
        Returns the estimated time in seconds until the task will be executed.
        """
        # Use a lock to ensure that only one thread modifies the queue at a time
        with self.lock:
            # Store the task along with its arguments as a tuple
            self.queue.append((task, args, kwargs))
            # Tell the processing thread that a new task is ready to be executed
            self.event.set()
            

    def _process_queue(self):
        """
        Continuously processes the tasks in the queue, ensuring the specified delay between the start times of consecutive tasks.
        """
        while True:
            # Wait for a task to be added to the queue
            self.event.wait()

            # Check the time since the last task and wait if necessary
            initial_wait = self._get_initial_wait()
            if initial_wait > 0:
                time.sleep(initial_wait)

            # Use the queue inside the lock to ensure that the queue is not modified by another thread
            with self.lock:
                if self.queue:
                    task, args, kwargs = self.queue.pop(0)
                    self.last_task_time = time.time()
                if not self.queue:
                    # No more tasks, clear the event to wait for the next task
                    self.event.clear()

            # Execute the task outside the lock to not block other operations
            task(*args, **kwargs)
