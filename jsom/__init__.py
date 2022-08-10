import argparse
import getpass
import re
import time

import pexpect
from pexpect import pxssh

CHANGED_HOST_KEY = re.compile(
    """@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\r\r
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @\r\r
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\r\r""")

NEW_HOST_KEY = re.compile(
    """The authenticity of host .* can't be established\.\r
ED25519 key fingerprint is .*\.\r
This key is not known by any other names\r
Are you sure you want to continue connecting \(yes/no/\[fingerprint\]\)\? """
)


class Defer:
    def __init__(self):
        self.defers = []
        self.was_run = False

    def add(self, statement):
        self.defers.append(statement)

    def run(self):
        if self.was_run:
            return

        for statement in reversed(self.defers):
            statement()
        self.was_run = True


def parse_args():
    parser = argparse.ArgumentParser(
        description="Connect to a Jupyter notebook server on SOM-HPC"
    )

    parser.add_argument("-a", "--address", help="address of ssh server", required=True)
    parser.add_argument("-u", "--username", help="ssh username", required=True)
    parser.add_argument("-k", "--key", help="private key file to use", required=True)
    parser.add_argument(
        "-c",
        "--conda",
        default="jupyter",
        help="conda environment containing jupyter server to activate",
        required=True,
    )

    return parser.parse_args()


def expect(address, username, pkey_file, conda_env):
    defer = Defer()
    print(f"Connecting to {username}@{address}")
    ssh = pxssh.pxssh(encoding="utf-8", options={"StrictHostKeyChecking": "no"})
    ssh.login(
        server=address, username=username, ssh_key=pkey_file, sync_original_prompt=False
    )
    print(f"Connected to {address}")
    ssh.sendline(f"conda activate {conda_env}")
    ssh.prompt()
    print(f'Activated "{conda_env}" conda environment')
    ssh.sendline("sbatch /data/shared/jobs/jupyter-notebook.job")
    try:
        ssh.expect(re.compile(r"Submitted batch job (\d+)\r\n"))
        job_id = ssh.match[1]
        ssh.prompt()
        print(f"Submitted job {job_id}")

        def deferD():
            ssh.sendline(f"rm jupyter-notebook.job.{job_id}")
            ssh.prompt()
            print(f"Deleted log from jupyter notebook job {job_id}")

        defer.add(deferD)

        def deferC():
            ssh.sendline(f"scancel -f {job_id}")
            ssh.prompt()
            print(f"Cancelled jupyter notebook job {job_id}")

        defer.add(deferC)

        job_info = ""

        # It might take a little bit for the notebook job to start, so
        # we "spin" until it does.
        while (local_tunnel := re.search("ssh -NL.*", job_info)) is None:
            time.sleep(2)
            ssh.sendline(f"cat jupyter-notebook.job.{job_id}")
            ssh.prompt()
            job_info = ssh.before

        local_tunnel = local_tunnel[0].strip()
        p = pexpect.spawn(local_tunnel, encoding="utf-8")
        print(f"Launched local ssh tunnel: {local_tunnel}")
        lt = p.expect(
            [
                CHANGED_HOST_KEY,
                NEW_HOST_KEY,
                pexpect.TIMEOUT,
            ],
            timeout=1
        )

        if lt == 0:
            warning = p.after
            p.expect("Host key verification failed.")
            raise Exception(f"\n\n{warning}{p.before}{p.after}\n\n")
        elif lt == 1:
            print(f"{p.before}{p.after}")
            result = input()
            p.sendline(result)
            if result.lower() != "yes":
                raise Exception("Rejected Host")
            p.expect("to the list of known hosts\.")

        def deferE():
            p.sendline("\x03")
            print("Cancelled local ssh tunnel")
        defer.add(deferE)

        inter_cmd = re.search("srun.*", job_info)[0].strip()
        ssh.sendline(inter_cmd)
        ssh.expect(re.compile("somhpc-execute"))
        print("Started SOM-HPC interactive session")

        def deferA():
            ssh.sendline("exit")
            ssh.prompt()
            print("Exited interactive session")

        defer.add(deferA)

        hpc_tunnel = re.search("ssh -NR.*", job_info)[0].strip()
        ssh.sendline(hpc_tunnel)
        ssh.expect("password:")
        hpc_pass = getpass.getpass("Password: ")
        ssh.sendline(hpc_pass)
        print(f"Launched SOM-HPC ssh tunnel: {hpc_tunnel}")

        def deferB():
            ssh.sendline("\x03")
            ssh.prompt()
            print("Cancelled SOM-HPC ssh tunnel")

        defer.add(deferB)



        jupyter_url = re.search("http://localhost:\d+", job_info)[0].strip()
        jupyter_password = re.search("password: (.*)", job_info)[1].strip()
        print("****************************")
        print("")
        print(f"Connect to Jupyter at: {jupyter_url}")
        print(f"The password is: {jupyter_password}")
        print("")
        print("****************************")
        time.sleep(60)
    except Exception as e:
        print(e)
    finally:
        defer.run()


def run():
    args = parse_args()

    expect(args.address, args.username, args.key, args.conda)
