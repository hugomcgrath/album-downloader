#!/bin/bash

conda env export | grep -v prefix > ../environment.yaml
conda env update -f ../environment.yaml --prune