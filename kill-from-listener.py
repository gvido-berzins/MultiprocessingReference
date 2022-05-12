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
