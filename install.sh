#!/bin/sh
if [ "$EUID" -ne 0 ]; then
	echo "install.sh requires superuser privelegies(it places a file to /usr/local/bin/)."
  echo "Run: sudo ./install.sh"
  exit 1
fi

chmod +x ./yatmpv.py
mv ./yatmpv.py /usr/local/bin/
mv ./yatmpv.css /usr/local/bin
echo "player succesfully installed!"
