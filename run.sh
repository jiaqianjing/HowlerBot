#/bin/bash
nohup python main.py >run.log 2>&1 &
echo $! > run.pid