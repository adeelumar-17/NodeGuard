#!/bin/bash

cd "$(dirname "$0")/.."

python3 -c "
from common.cert_generation import generate_certificates
paths = generate_certificates()
print('Generated certificates:')
for name, path in paths.items():
    print(f'  {name}: {path}')
"