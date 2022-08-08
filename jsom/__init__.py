import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Connect to a Jupyter notebook server on SOM-HPC")

    parser.add_argument("-a", "--address", help="address of ssh server", required=True)
    parser.add_argument("-u", "--username", help="ssh username", required=True)
    parser.add_argument("-k", "--key", help="private key file to use", required=True)
    parser.add_argument("-c", "--conda", default="jupyter", help="conda environment containing jupyter server to activate", required=True)

    return parser.parse_args()

def expect(address, username, pkey_file, conda_env):
    pass

def run():
    args = parse_args()

    expect(args.address, args.username, args.key, args.conda)
