import argparse
import re
import time

from pexpect import pxssh


def parse_args():
    parser = argparse.ArgumentParser(description="Connect to a Jupyter notebook server on SOM-HPC")

    parser.add_argument("-a", "--address", help="address of ssh server", required=True)
    parser.add_argument("-u", "--username", help="ssh username", required=True)
    parser.add_argument("-k", "--key", help="private key file to use", required=True)
    parser.add_argument("-c", "--conda", default="jupyter", help="conda environment containing jupyter server to activate", required=True)

    return parser.parse_args()

def expect(address, username, pkey_file, conda_env):
    print(f"Connecting to {username}@{address}")
    ssh = pxssh.pxssh(encoding="utf-8", options={
        "StrictHostKeyChecking": "no"
    })
    ssh.login(server=address, username=username, ssh_key=pkey_file, sync_original_prompt=False)
    print(f"Connected to {address}")
    ssh.sendline(f"conda activate {conda_env}")
    ssh.prompt()
    print(f"Activated \"{conda_env}\" conda environment")
    ssh.sendline("sbatch /data/shared/jobs/jupyter-notebook.job")
    ssh.expect(re.compile(r"Submitted batch job (\d+)\r\n"))
    job_id = ssh.match[1]
    ssh.prompt()
    print(f"Submitted job {job_id}")

    time.sleep(2)

    ssh.sendline(f"cat jupyter-notebook.job.{job_id}")
    ssh.prompt()
    job_info = ssh.before
    run = re.search("srun.*", job_info)[0].trim()
    hpcTunnel = re.search("ssh -NR.*", job_info)[0].trim()
    localTunnel = re.search("ssh -NL.*")[0].trim()
    jupyterPassword = re.search("password: (.*)")[1].trim()


    ##
    ## Clean Up
    ##
    ssh.sendline(f"scancel -f {job_id}")
    ssh.prompt()
    print(f"Cancelled jupyter notebook job {job_id}")
    ssh.sendline(f"rm jupyter-notebook.job.{job_id}")
    ssh.prompt()
    print(f"Deleted log from jupyter notebook job {job_id}")

def run():
    args = parse_args()

    expect(args.address, args.username, args.key, args.conda)
