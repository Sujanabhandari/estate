#!/bin/bash
pip3 install --upgrade pip
pip3 install -r dev/requirements.txt
git submodule update --init
git update-index --assume-unchanged config/* dev/*
chmod +x ../dev.sh
