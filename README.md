## Hardware preparations

- Tested on a Raspberry Pi 1 Model B using Raspbian 9.1
- The door lock is opened by raising a single GPIO pin
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

## References

- [wiringPi wiring scheme][1]
- [The `gpio` utility][2]
- [Bash exit traps][3]

[1]: https://pinout.xyz/pinout/wiringpi
[2]: https://projects.drogon.net/raspberry-pi/wiringpi/the-gpio-utility/
[3]: http://redsymbol.net/articles/bash-exit-traps/
