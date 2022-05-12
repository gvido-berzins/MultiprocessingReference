Run a process in parallel

```python
def job_executor():
    print("Executor started")


def cancellator():
    """Cancellation listener"""
    print("Cancellator started")


def reporter():
    """Status update subprocess"""
    print("Reporter started")


def main():
    # MAIN process
    executor_process = Process(target=job_executor)
    cancel_process = Process(target=cancellator)
    reporter_process = Process(target=reporter)
    processes = [executor_process, cancel_process, reporter_process]
    for p in processes:
        p.start()
```

Kill a running process based on timeout
```python
import time
from multiprocessing import Process

TTL = 3


def job_executor():
    print("Executor started")
    time.sleep(30)


def main():
    # MAIN process
    process = Process(target=job_executor)
    process.start()
    time_started = time.time()

    while True:
        if not process.is_alive():
            print("Process dead, nothing to do.")
            break

        processing_time = time.time() - time_started
        if processing_time > TTL:
            print(f"Killing process: {process.pid}")
            process.kill()
            time.sleep(1)  # Wait a bit for it to die


if __name__ == "__main__":
    main()
```

Kill a running process from a message in a shared queue/channel
```python
import time
from multiprocessing import Process, Queue

import psutil

ProcessID = int


def job_executor():
    """It's just doing it's job"""
    print("~> Executor started")
    while True:
        try:
            time.sleep(60)
        except Exception as e:
            print(e)


def listener(kill_channel: Queue):
    """Listener listens for kill items and kills the given pid"""
    print("~> Listener started")
    while True:
        pid = kill_channel.get()
        print(f"Given PID: {pid}")
        try:
            # Thows NoSuchProcess if is dead or doesn't exist
            process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            print("Process dead, nothing to do.")
        else:
            print(f"Killing process: {process}")
            process.kill()
            break


def killer(pid_channel: Queue, kill_channel: Queue):
    """Killer places the pid from pid channel into the kill chanel"""
    print("🔪 Killer on the loose 🔪")
    time.sleep(2)
    pid_to_kill = pid_channel.get()
    kill_channel.put(pid_to_kill)
    print("# It's done.")


def main():
    # MAIN process
    kill_channel = Queue()
    pid_channel = Queue()
    executor_process = Process(target=job_executor)
    executor_process.start()
    pid_channel.put(executor_process.pid)

    listener_process = Process(target=listener, args=(kill_channel,))
    listener_process.start()

    killer_process = Process(target=killer, args=(pid_channel, kill_channel))
    killer_process.start()


if __name__ == "__main__":
    main()
```

Determine how it was killed (return code, cancellation message contents)
```python
# If the multiprocessing.Process object is available
exit_code = process.exitcode
print(f"Process exit code: {exit_code}")
```

Communicate between 2 processes (queues/channel)
- same queue is shared between processes
- get, put messages (if logic needs after checking if the queue has items, use `queue.get(block=False)` in while loop, throws `queue.Empty` exception)
```python
import time
from dataclasses import dataclass
from multiprocessing import Process, Queue
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
RESULTS_PATH = SCRIPT_DIR / "results.txt"


@dataclass
class Job:
    id: str
    data: list[int]

    def __str__(self):
        return f"ID {self.id}: Size {len(self.data)}"


def job_executor(job_channel: Queue, status_channel: Queue):
    """Job processor, reports statuses back to reporter"""
    print("~> Executor started")
    while True:
        job = job_channel.get()
        print(f"Processing job: {job}")
        time.sleep(0.5)
        results = sum(job.data)
        status = dict(id=job.id, results=results)
        status_channel.put(status)


def loader(job_channel: Queue):
    """Job loader, gives jobs to the job_executer"""
    print("~> Cancellator started")
    for i in range(1, 6):
        job = Job(id=str(i), data=[6] * i)
        print(f"Job {job}, ready!")
        job_channel.put(job)


def reporter(status_channel: Queue):
    """Status update subprocess

    Dumps all results into the project directory file 'results.txt'"""
    print("~> Reporter started")
    RESULTS_PATH.write_text("")
    while True:
        results = status_channel.get()
        with RESULTS_PATH.open("a") as f:
            f.write(f"{results}\n")


def main():
    # MAIN process
    job_channel = Queue()
    status_channel = Queue()
    executor_process = Process(target=job_executor, args=(job_channel, status_channel))
    loader_process = Process(target=loader, args=(job_channel,))
    reporter_process = Process(target=reporter, args=(status_channel,))
    processes = [executor_process, loader_process, reporter_process]
    for p in processes:
        p.start()


if __name__ == "__main__":
    main()

```