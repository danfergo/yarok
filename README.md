# YAROK - Yet another robot framework

A tiny library for building robot devices, robots and robotic environments.

Aimed for quick prototyping, learning, researching, etc. \
For running in simulation and/or real robots.   

Write self-contained components () for representing 

### Install
    
```
    pip3 install yarok
```

run the EmptyWorld example from the terminal,
```
    yarok run EmptyWorld
```

and/or from code,
``` 
    # main.py
    yarok.run(EmptyWorld, {
        'platform_args': {
            'viewer_mode': sys.argv[1]
        }
    })
```
```
    yarok run main
```

checkout the ready to go example [components](#components):

Sensors and Actuators
* (Generic) Camera
* Gelsight 

### Getting started
