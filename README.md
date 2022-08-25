
# JSOM
Expect script for connecting to Jupyter notebooks on DASH/SOM-HPC

### Install

To install jsom run:

```sh
git clone https://github.com/ReddyLab/jsom.git
cd jsom
make install
```

### Prerequisites

* Python 3.8
* Public key authentication [set up for DASH/SOM-HPC](https://github.com/ReddyLab/jsom/wiki/Setting-up-a-SOM-HPC-account-to-use-public-key-authentication)

This should work on Mac, may work on Linux, and probably doesn't work on Windows.

### Uninstall

```sh
make uninstall
```

### Usage

    jsom [-h] -a ADDRESS -u USERNAME -k KEY -c CONDA [-m MEM] [-t TIME] [--cpus-per-task CPUS_PER_TASK]

### Options

    -h, --help                       show this help message and exit
    -a ADDRESS, --address ADDRESS    address of ssh server
    -u USERNAME, --username USERNAME ssh username
    -k KEY, --key KEY                private key file to use
    -c CONDA, --conda CONDA          conda environment containing jupyter server to activate
    -d, --debug                      echo all output to stdout
    -m MEM, --mem MEM                amount of memory allocated to jupyter job
    -t TIME, --time TIME             amount of time jupyter job will be allowed to run
    --cpus-per-task CPUS_PER_TASK    number of CPUs allocated to jupyter job
