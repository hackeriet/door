# door

GPIO door lock control

- Tested on a Raspberry Pi 1 Model B using Raspbian 9.1
- The door lock is triggered by raising a single GPIO pin
- Pins are numbered using the [wiringPi scheme][1]

## Installing

    # apt install wiringpi
    # curl -sSfo /usr/bin/open-door https://raw.githubusercontent.com/hackeriet/door/master/open-door

## Usage

Configurable environment variables and their defaults:

  - `GPIO_PIN_DOOR=0` GPIO pin to trigger door lock
  - `STAY_UNLOCKED_SEC=2` How long should the pin be kept high

Trigger the door lock

```
$ GPIO_PIN_DOOR=0 STAY_UNLOCKED_SEC=2 open-door
```

## Trigger lock over network

### SSH

Connect with SSH from the local network and use the password stored from hackerpass `infrastructure/entry@humladoor-new.haus.hackeriet.no`.

```
$ ssh entry@10.10.3.15 open-door
```

Using a static IP as there seems to be some problems with hostname resolution at the moment. The hostname of this system will eventually change anyway.

### Web interface

Username and password in `hackerpass door-remote.hackeriet.no`

https://door-remote.hackeriet.no

## References

- [wiringPi wiring scheme][1]
- [The `gpio` utility][2]
- [Bash exit traps][3]

[1]: https://pinout.xyz/pinout/wiringpi
[2]: https://projects.drogon.net/raspberry-pi/wiringpi/the-gpio-utility/
[3]: http://redsymbol.net/articles/bash-exit-traps/
