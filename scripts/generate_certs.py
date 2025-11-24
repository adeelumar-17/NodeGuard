#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.cert_generation import generate_certificates


def main():
    paths = generate_certificates()
    print('Generated certificates:')
    for name, path in paths.items():
        print(f'  {name}: {path}')


if __name__ == '__main__':
    main()