import time
from multiprocessing import Process


def job_executor():
    print("Executor started")
    time.sleep(1)


def cancellator():
    """Cancellation listener"""
    print("Cancellator started")
    time.sleep(5)


def reporter():
    """Status update subprocess"""
    print("Reporter started")
    time.sleep(3)


def main():
    # MAIN process
    executor_process = Process(target=job_executor)
    cancel_process = Process(target=cancellator)
    reporter_process = Process(target=reporter)
    processes = [executor_process, cancel_process, reporter_process]
    for p in processes:
        p.start()

    monitor_running_processes(processes)


def monitor_running_processes(processes: list[Process]):
    print("MONITORING".center(70, "-"))
    while True:
        time.sleep(1)
        if not processes:
            break

        for process in reversed(processes):
            if process.is_alive():
                print(f"{process.name}: Alive")
            else:
                print(f"{process.name}: Dead")
                processes.remove(process)

    print("END".center(70, "-"))


if __name__ == "__main__":
    main()
