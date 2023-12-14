from redis import Redis
from rq import Queue
from rq.worker import Worker
from rq.command import send_shutdown_command
from uuid import uuid4

from dotenv import load_dotenv
import os , signal
import subprocess

import argparse


load_dotenv(".env/.mq.env")
redis_url = os.getenv("REDIS_URL")
queue_name = os.getenv("QUEUE_NAME")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Worker manager.")

    mode = parser.add_argument_group(title="Worker Mode", description="Worker Mode")
    # start or stop
    mode.add_argument("action", help="Start or stop workers.",choices=["start","stop","status"])
    # n : total workers 
    count_group = parser.add_argument_group(title="Specify worker amount", description="Specify worker amount")
   
    count_group.add_argument("--all", help="Stop all workers.",action="store_true")
    count_group.add_argument("-n", help="Specific amount of workers.",default=1)


    args = parser.parse_args()

    redis_connection = Redis.from_url(redis_url)
    queue = Queue(queue_name, connection=redis_connection)

    if args.action == "start":  
        n = int(args.n)
        for i in range(n):
            # run `rq worker rq` command
            subprocess.Popen(
                ["rq","worker",queue_name,"--name",f"worker-{uuid4().hex[:4]}","--with-scheduler"],
                env={
                    **os.environ,
                    "OBJC_DISABLE_INITIALIZE_FORK_SAFETY":"YES",
                    "NO_PROXY":"*"
                }
            )

        print(f"Start {n} workers.")

    elif args.action == "stop":
        if args.all:
            workers = Worker.all(queue=queue)
            for worker in workers:
                pid = worker.pid
                print(f"Stop {worker.name} [{pid}]")
                worker.register_death() # delete worker from redis in 60 seconds
                send_shutdown_command(connection=redis_connection,worker_name=worker.name)

    elif args.action == "status":
        workers = Worker.all(queue=queue)
        for worker in workers:
            print(f"{worker.name} is {worker.get_state()}")


    else:
        print("No mode selected.")
        exit(1)