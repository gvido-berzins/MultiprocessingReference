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
