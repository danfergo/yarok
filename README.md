# YAROK - Yet another robot framework

[![PyPI Version](https://img.shields.io/pypi/v/yarok.svg?color=blue)](https://pypi.python.org/pypi/yarok)

Is a **Python** library for interfacing with sensors and actuators, and composing robots and robotic environments.
Aimed for quick prototyping, learning, researching, etc. Simulation first (MuJoCo).

It can be seen as a minimalistic alternative to ROS: Python-centric, OS independent and single process.

It is centered around modularity for reusability: 
each component is self-contained with a template, an environment-independent 
controller Python class and interfaces for handling each environmnent (MuJoCo or real). 
It supports nesting an existing component onto another e.g. a gripper onto a robot arm. 



Checkout the **[Demo](https://github.com/danfergo/yarok-demo)** repository, and start coding your next project.

## Install


```
    pip3 install yarok
```

run an example world and behaviour,

``` 
    # test.py
    
    from yarok import Platform
    from yarok.examples.grasp_rope_world import GraspRopeWorld, GraspRopeWorld
    
    Platform.create({
        'world': GraspRopeWorld,
        'behaviour': GraspRoleBehaviour
    }).run()
```

```
  python -m test
```

Try other worlds

| Name                                             | Description  |
|:-------------------------------------------------|---|
| [EmptyWorld](yarok/comm/worlds/empty_world.py)   | Just an empty world. Can be used as the base for other worlds.
| [DigitWorld](yarok/comm/worlds/digit_world.py)   | A Pick and Place with a UR5 arm, Robotiq gripper, and the DIGIT tactile sensor
| [GelTipWorld](yarok/comm/worlds/geltip_world.py) | A UR5 arm and Robotiq 2 finger gripper, equipped with GelTip sensors, pulling a rope

##### Other projects using Yarok
If you are using yarok, let us know.

| Name                                                       | Description  |
|:-----------------------------------------------------------|---|
| [GelTipSim](https://github.com/danfergo/geltip-simulation) |  GelTip simulation model project
| [ModoVT](https://github.com/danfergo/modovt)               | (WIP) Manipulation of Deformable Objects using vision and Touch
| [AtWork](https://github.com/danfergo/atwork)               | (WIP) Playground for experimenting with manipulation and mobile robots, feat [RoboCup@Work](https://atwork.robocup.org/)


## Example components

Example components are included in this package to reduce any friction with getting started with the library, if
you would like us to include/reference yours let us know.

You can import these components into your world/component as follows. (see the example worlds)

```
    from yarok.comm.components.abc_xyz.abc_xyz import AbcXyz
    
    @component(
        ...
        components=[
            AbcXyz
        ],
        template="""
            <mujoco>
                <worldbody>
                    <abc-xyz />            
        """
```

###### Sensors

| Name                                                           | Description  |
|:---------------------------------------------------------------|---|
| [Cam](yarok/comm/components/cam/cam.py)                        | Wraps the py_mujoco and OpenCV APIs for handling generic cameras.
| [Digit](yarok/comm/components/digit/digit.py)                  | DIGIT optical tactile sensor, [Lambeta et al.](https://digit.ml/). Simulation model and assets ported from [Zhao et. al](https://github.com/Rancho-zhao/Digit_PhongSim).                                      
| [GelSight2014](yarok/comm/components/gelsight/gelsight2014.py) | (WIP) tactile sensor as proposed in [Rui Li et al.](http://persci.mit.edu/publications/rui-iros2014) and the simulation model proposed in [Gomes et al.](https://danfergo.github.io/gelsight-simulation/)
| [GelTip](yarok/comm/components/geltip/geltip.py)               | (WIP) Finger-shaped tactile sensor, [Gomes et al.](https://danfergo.github.io/geltip/), and simulation model [GelTip Simulation](https://github.com/danfergo/geltip-simulation)

###### Actuators

| Name                                                              | Description  |
|-------------------------------------------------------------------|---|
| [AnetA30](yarok/comm/components/anet_a30/anet_a30.py)             | FFF 3D printer modeled after the Geeetech ANET A30 (or Creality CR-10) to be used as 3 DoF a cartesian actuator. Real hardware via [serial](https://github.com/pyserial/pyserial) (USB).
| [UR5](yarok/comm/components/ur5/ur5.py)                           | The 6 DoF [Universal Robots UR5](https://www.universal-robots.com/products/ur5-robot/). Real hardware via [python-urx](https://github.com/SintefManufacturing/python-urx) library.
| [Robotiq2f85](yarok/comm/components/robotiq_2f85/robotiq_2f85.py) | The [Robotiq 2F-85 gripper](https://robotiq.com/products/2f85-140-adaptive-robot-gripper). Real hardware via [python-urx](https://github.com/SintefManufacturing/python-urx) and the UR5 computer.


## Write your first Component

**Components** can be used to represent robot parts (sensors or actuators), robots, or an entire world.

```
from yarok import component, Injector
from yarok.comm.worlds.empty_world import EmptyWorld

@component(
    tag='some-component',
    extends=EmptyWorld,
    components=[
        OneSubcomponent,
        AnotherSubcomponent
    ],
    defaults={
      'interface_mjc': SomeComponentInterfaceMJC,
      'interface_hw': SomeComponentInterfaceHW,
      'a_config: 'a_value'
    },
    # language=xml
    template="""
    <mujoco>
       <worldbody>
          <body> .... </body>
          <one-subcomponent name='sub'>
             <another-subcomponent name='subsub' parent='body-in-parent'/>
             ...
          </one-subcomponent>
       </worldbody>
       <actuator> ... </actuator>
       <sensor> ..  <sensor>
   </mujoco>
    """
)
class SomeComponent

    def __init__(sub: OneSubcomponent, injector: Injector):
        self.sub = sub
        self.subsub = injector.get('subsub')
    
    def do_something_else(args):
        this.sub.do_it()
        this.subsub.do_it_also()
    
    def do_something_else(pos):
        # implemented by the interface
        pass 
```

What to know when coding a **Component decorator** and **class**

| Name        | Description                                                                                                                                                                                                                                                                                                                                                                                    |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| tag         | To be used as the tag in the .xml templates.                                                                                                                                                                                                                                                                                                                        |
| extends     | References the parent template. This component body is appended to the "parent" body.
| Components  | References to the classes/components to be used as subcomponents in this component.
| Defaults    | Configs that can be referenced in the template using ``${conf}``, and can be (re)configured when launching the platform. 
| Interfaces  | MuJoCo ``interface_mjc`` or Real Hardware ``interface_hw`` interfaces, used to interface with the real/sim platforms. Before instantiating the component, Yarok merges the appropriate environment interface with the component class, effectively becoming one. Thus, the component class should declare the interface(s) common public methods (api) as empty/pass for static typing.
| Template    | The component is described in .xml, using the MJCF format (from MuJoCo), with aditional options for component composition and passing variables. At runtime, Yarok handles the nesting of components, renaming / namespacing to avoid name collisions. (# language=xml can be prepended for syntax highlight in PyCharm) 
| Class       | The Python class used to interface with the component programmatically.                                                                                                                                                                                                                                                                                                                        |
| Constructor | You can "request" the reference of the instantiated (sub)components in the template, by adding ` name: ComponentClass ` to the constructor arguments. You can also request the injector ``injector: Injector`` and then call ``injector.get(name)``.

### Using a component within another component
```
<another-subcomponent name='subsub' parent='body-in-parent'/>
```

| Name     | Description                                                                                              |
|----------|----------------------------------------------------------------------------------------------------------|
| tagname | The name of the component, declared in the component decorator `tag`                                     |
| @name    | The name/id of the component instance.
| @parent  | (optional) When sub-nesting (check example) you can use the @parent attribute to reference the parent body in the parent component, wherein the subcomponent will be nested. Make sure that a body with such name existis in the parent component.

### Eval

```
  <geom pos="
            ${0.5 + 0.082*x if z % 2 == 0 else 0.58} 
            ${0.48 if z % 2 == 0 else 0.4 + 0.082*x}
            ${0.061*z}" />
```
You can use `${}` to have python expressions evaluated within the template. 
You can use variables here, from the config/defaults or the tree context.
### If block and attribute
```
<if the='x == 4'>
  ...
</for>

<geom if="y == 2" .../>
```
The if block / attribute. You can use variables here.

### For loop
```
<for each='range(n_elements)' as='i'>
  ...
</for>
```
``each`` a python expression that returns an iterable, you can use variables here. 
``as`` is the name of the iterable. You'll be able to use it in the evals/ifs/fors down the chain.
[usage example](yarok/comm/toys/tumble_tower/tumble_tower.py#L25)  

⚠ All paths for meshes are relative to the component directory.

Here we described the extensions on top of the MJCF language, for the full reference check
the [MuJoCo XML](https://mujoco.readthedocs.io/en/latest/XMLreference.html).


### Interface with Sim or Real sensors or actuators

To directly interact with sensors or actuators, you should write an Interface.

###### The MuJoCo Interface

```
from yarok.mjc.interface import InterfaceMJC

@interface(
  defaults={
    'some_config': 'some_value'
  }
)
class SomeComponentInterfaceMJC:
    
    def __init__(self, interface: InterfaceMJC):
        self.interface = inteface
        self.pos = 0

    def step():
        self.interface.set_ctrl(0, self.pos)
        
    def do_something_else(pos):
        self.pos = pos
    
```

| Name        | Description                                                                                                                       |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------|
| constructor | Receives as argument an instance of `InterfaceMJC` to be used to interface with MuJoCo.                                          |
| step()      | (optional) This method is called every update step of the simulation, and can be used to read from or update the simulation state.

InterfaceMJC useful methods:

| Name             | Description                                                                                                                        |
|------------------|------------------------------------------------------------------------------------------------------------------------------------|
| set_ctrl(k,v)    | Sets the control of an actuator. `k` is the index or name of the actuator. `v` is the control value.                               |
| sensordata()     | Returns the data from the sensors in the component.
| read_camera(...) | Reads a raw MuJoCo camera specified in the component template. `camera_name` is the name of the camera, `shape=(480,640) is the size of the returned image (numpy style),  `depth=False` and `rgb=True` indicate whether you want the rgb and/or depth to be returned. The depth is in meters (and not in z-buffer format, as in the raw mujoco api)

Check the InterfaceMJC implementation/API [here](yarok/platforms/mjc/interface.py).

###### The Real Hardware Interface

(check out existing interfaces for reference.)
```
class SomeComponentInterfaceHW:
    
    def step():
       # call some serial api etc.
       
   def do_something_else(pos):
        self.pos = pos     
```


## Run your world component

In a "write once run everywhere" fashion, Yarok allows you to setup platform specific or platform shared configurations.

Config example / schema.

```
conf = {
    'world': SomeWorld,    # class ref of the world/root component
    'behaviour': GraspRoleBehaviour,
    'environment': 'sim',
    'defaults': {
        'behaviour': {
            'conf1': 'value'
            ...
        },
        # configs to be passed to the component constructor,
        # and/or template
        'components': {
            # path to the component, in the tree of components. 
            # '/' would be the root component / world
            '/': { 
                'confx': 'valuex'
            },
            # sub component named 'sub' in the root component.
            '/sub': {
                'confy': 'valuey'
            },
            # and so forth.. (subsub inside sub)
            '/sub/subsub': {
                'confz': 'valuez'
            }
        },
        # pluggins that can be called at every step of the control loop
        'plugins': [
            Cv2Inspector(),
        ]
    },
    # environment specific configurations.
    # These are choosen depending on the 'environment' setting above and override the defaults.
    'environments': {
        'sim': {
            'platform': {
                'class': PlatformMJC
            },
            'behaviour': {
                'where_iam': 'In Simulation !'
            },
            'interfaces': {
                 '/sub/subsub': {
                     'serial_path': '/dev/ttyUSB0'
                 },
            }
        },
        'real': {
            'platform': PlatformHW,
            'behaviour': {
                'where_iam': 'In The Real World !'
            },
            'interfaces': {
                 '/sub/subsub': {
                     'serial_path': '/dev/ttyUSB0'
                 },
            }
        }
    },
}
```

```
Platform.create(conf).run()
```

## Let's make your robot move

To make your robot do something useful, and keep it separate from world code, you should write a
behaviour class. In the constructor you can request the same (sub)components as in the World component.

```
from yarok import Platform

class SomeBehaviour:
    
    def __init__(self, robot: SomeRobot, pl: Platform):
        self.robot = robot
        self.pl = pl
        
    def on_start():
        pass
                
    def on_update():
        self.robot.go(100)
        self.pl.wait(lambda: self.robot.at(100))
        
        self.robot.go(10)
        self.pl.wait(lambda: self.robot.at(10))
        
```

Yarok is single threaded, therefore if you write a loop to wait for anything/seconds, you'll lock the running loop,
stopping the simulation and the ``step()`` calls.
Therefore, when your Behaviour needs to wait for something you should use

| Name                | Description                                                                                                     |
|---------------------|-----------------------------------------------------------------------------------------------------------------|
| wait(fn, cb)        | waits until ``fn`` returns ``True``. ``cb`` can be used to do stuff every step, such as logging/plotting images
| wait_seconds(s, cb) | waits ``s`` seconds                                                                                                    |
| wait_forever(cb)    |                                                                                                                 |
| wait_once()         |                                                                                                                 |

## Plugins

Plugins can be used to extend yarok further with everything "meta".
Current plugins

| Name             | Description                                                                                                                                                                                                                |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CV2WaitKey       | Calls ``cv2.waitKey(1)`` every step of the control loop, so that you can use ``cv2.imshow`` in your components/behaviours.                                                                                                 
| CV2Inspector     | Iterates through all components and calls `probe(component)` method declared in the component defaults/config. The returned data is displayed as OpenCV frames (when using CV2Inspector, you don't need to use CV2WaitKey) |

A Plugin, can be any Python class that implements a ``step()`` method.

## Quick bugfixes

- If having conflicts after installing **cv2**, comment import imageio
- On MuJoCo 1.0 (pre deepmind aquisition), the following
  export ``export LD_PRELOAD='/usr/lib/x86_64-linux-gnu/libGLEW.so' `` was used to successfully have the simulation
  running with the GPU.


## Todo list
- Update PlatformHW to use @interface defaults
- Add probe to interface decorator
- Behaviour to each component vs single behaviour. (Problems with platform.wait?) 
- Handle/rename MuJoCo defaults / classes  
- Handle compiler options
- Verify schema/that configs for interfaces can be passed on
- Review documentation README.md
- Add support for mujoco's include
