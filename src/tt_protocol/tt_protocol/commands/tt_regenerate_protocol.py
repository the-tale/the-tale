
import os

import argparse
import subprocess


PROJECT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')

SOURCE_DIR = os.path.join(PROJECT_DIR, 'source')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'protocol')

parser = argparse.ArgumentParser(description=u'Regenerate protocol buffers python code')


def main():
    parser.parse_args()

    files = ('base.proto',
             'diary.proto',
             'personal_messages.proto',
             'storage.proto',
             'market.proto',
             'bank.proto',
             'timers.proto',
             'impacts.proto',
             'events_log.proto',
             'properties.proto',
             'matchmaker.proto',
             'effects.proto',
             'uniquer.proto',
             'discord.proto')

    files = [os.path.join(SOURCE_DIR, filename) for filename in files]

    subprocess.run('protoc  --proto_path="{source_dir}" --python_out="{output_dir}" {files}'.format(source_dir=SOURCE_DIR,
                                                                                                    output_dir=OUTPUT_DIR,
                                                                                                    files=u' '.join(files)),
                   shell=True, check=True)
