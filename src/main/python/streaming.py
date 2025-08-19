from typing import Callable

import multiprocessing as mp

class SequentialStreamingExecutor[T]:
    """
    Executor that streams results sequentially from a task.
    """

    def __init__(self, task: Callable[[int], tuple[int, T]], count: int):
        """
        Initializes the executor with a task to execute.

        Starts a multiprocessing pool and a manager to handle shared state.

        :param task: A callable that takes an integer (the task index) and returns a result.
        :param count: The number of tasks required to execute.
        """
        self.manager = mp.Manager()
        self.shared_dict = self.manager.dict()
        self.condition = self.manager.Condition()
        self.pool = mp.Pool(processes=12)
        self.count = count

        def done(result: tuple[int, T]):
            task_id, output = result
            # print(f"Item {task_id} done")
            try:
                with self.condition:
                    self.shared_dict[task_id] = output
                    self.condition.notify_all()
            except EOFError:
                # Closed semaphore
                pass

        for task_id in range(self.count):
            self.pool.apply_async(
                task,
                args=(task_id,),
                callback=done,
                error_callback=lambda e: print(f"Error in task {task_id}: {e}")
            )
        self.pool.close()

    def stream(self):
        """
        Generator that yields results as they become available.

        :return: A generator yielding lists of particles.
        """
        next_id = 0
        while next_id < self.count:
            try:
                with self.condition:
                    # print(f"Waiting for item {next_id}")
                    self.condition.wait_for(lambda: next_id in self.shared_dict)
                    result = self.shared_dict.pop(next_id)
                    # print(f"Item {next_id} consumed")
                    next_id += 1
                    yield result
            except FileNotFoundError:
                # If the pool is closed, we stop yielding results
                break

    def close(self):
        self.pool.terminate()
        self.manager.shutdown()
        # print("StreamingExecutor closed.")
