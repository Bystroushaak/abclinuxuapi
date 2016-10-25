#! /usr/bin/env bash
export PYTHONPATH="src:$PYTHONPATH"
python -m pytest tests/ $@