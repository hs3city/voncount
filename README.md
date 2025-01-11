## Count von count

![Count](https://upload.wikimedia.org/wikipedia/en/2/29/Count_von_Count_kneeling.png)

This repo uses the stock YOLOv5 to create a people counter on a Raspberry Pi 3.
It takes a picture from the pi camera (or possibly USB cam will work too, but not tested),
and runs YOLOv5 on it.

In then get the tags we're interested in (persons ~~and pizzas~~ -- unfortunately we didn't get it to count pizzas....).
It displays the number of people on a [7 segment display](https://www.sparkfun.com/products/8546) connected to the GPIO pins (the middle pins to +3.3V, the rest of the pins have to be mapped in count.py; these pins were chosen so that they are all on inner-row of the GPIO headers), as a hex value between 0 and F.

Obviously from here you can do what you want with the data (e.g. send it to ~~discord server~~ mqtt server, after which it goes to discord).

The system runs on balena (Raspberry pi 3 64-bit, OS version balenaOS 6.1.24+rev1, supervisor version 16.10.3).
Just make sure you set `BALENA_HOST_CONFIG_camera_auto_detect=1` in balena configuration.



The system was created for internal use in [Hackerspace Trójmiasto](https://hs3.pl).


More info (blog posts / photo's / etc) will follow.
