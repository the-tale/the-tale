
import os

import argparse
import subprocess


PROJECT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')

SOURCE_DIR = os.path.join(PROJECT_DIR, 'source')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'protocol')

parser = argparse.ArgumentParser(description=u'Regenerate protocol buffers python code')


def main():
    parser.parse_args()

    files = [os.path.join(SOURCE_DIR, filename)
             for filename in os.listdir(SOURCE_DIR)
             if filename.endswith('.proto')]

    subprocess.run('protoc  --proto_path="{source_dir}" --python_out="{output_dir}" {files}'.format(source_dir=SOURCE_DIR,
                                                                                                    output_dir=OUTPUT_DIR,
                                                                                                    files=u' '.join(files)),
                   shell=True, check=True)
