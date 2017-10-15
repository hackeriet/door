# Raspberry Pi 3 w/Raspbian

Do a fresh install then remove some unwanted/-needed services.

    # echo 'dtoverlay=pi3-disable-bt-overlay' | sudo tee -a /boot/config.txt
    # apt-get remove bluez
    # apt-get autoremove
    # apt-get install vim git
