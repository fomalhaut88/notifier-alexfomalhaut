#!/bin/bash

python api.py &
P1=$!
python bot.py &
P2=$!
wait $P1 $P2
