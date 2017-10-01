chdir () {
  cd /home/pi/APM-Control
}

until ping -c1 8.8.8.8 &>/dev/null; do :; done

chdir
python ./src/main.py
