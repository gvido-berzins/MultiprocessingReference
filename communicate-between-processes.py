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
