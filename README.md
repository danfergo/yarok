# YAROK - Yet another robot framework

A **Python** library for interfacing with sensors and actuators, and composing robots and robotic environments.
Aimed for quick prototyping, learning, researching, etc.

Key features of **Yarok**:
* Modularity through components.
* Environment independent control logic.

With **Yarok** you can:
* Write driver components, for sensors and actuators, with different interfaces for real world and MuJoCo environments.
* Compose robots and robotic environments from driver components.
* Use components from others and/or share your own.
* Write generic python scripts for controlling such robots e.g. RL Algorithms.
* Run experiments in simulation (in MuJoCo) and/or real robots interchangeably.   

## Install
    
```
    pip3 install yarok
```

run the EmptyWorld example from the terminal,
```
    yarok run EmptyWorld
```

or from code,
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

## Example components
We host here some components for reducing any friction with getting started with the library, if you would like us to include/reference yours here let us know.

###### Sensors

| Name   | Description  |
|:---|---|
| cam | Wraps the py_mujoco and OpenCV APIs for handling generic cameras.
| gelsight2014 | The optical tactile sensor as proposed in [Rui Li et al.](http://persci.mit.edu/publications/rui-iros2014) and the simulation model proposed in [Gomes et al.](https://danfergo.github.io/gelsight-simulation/)
| geltip  | The finger-shaped tactile sensor as proposed in [Gomes et al.](https://danfergo.github.io/geltip/) and simulation model 

###### Actuators
| Name   | Description  |
|---|---|
| anet_a30     | FFF 3D printer modeled after the Geeetech ANET A30 (or Creality CR-10) to be used as 3 DoF a cartesian actuator. Real hardware via [serial](https://github.com/pyserial/pyserial) (USB).
| ur5          | The 6 DoF [Universal Robots UR5](https://www.universal-robots.com/products/ur5-robot/). Real hardware via [python-urx](https://github.com/SintefManufacturing/python-urx) library.
| robotiq_2f85 | The [Robotiq 2F-85 gripper](https://robotiq.com/products/2f85-140-adaptive-robot-gripper). Real hardware via [python-urx](https://github.com/SintefManufacturing/python-urx) and the UR5 computer.

###### Environments
| Name   | Description  |
|---|---|
| anet_a30     | FFF 3D printer modeled after the Geeetech ANET A30 (or Creality CR-10) to be used as 3 DoF a cartesian actuator. Real hardware via [serial](https://github.com/pyserial/pyserial) (USB).
| ur5          | The 6 DoF [Universal Robots UR5](https://www.universal-robots.com/products/ur5-robot/). Real hardware via [python-urx](https://github.com/SintefManufacturing/python-urx) library.
| robotiq_2f85 | The [Robotiq 2F-85 gripper](https://robotiq.com/products/2f85-140-adaptive-robot-gripper). Real hardware via [python-urx](https://github.com/SintefManufacturing/python-urx) and the UR5 computer.


## Getting started

The key concept in Yarok is the component. A component represents one part of your robotic setup, and is composed of:

| Name   | Description  |
|---|---|
| Model description | The component is described/modeled in .xml, using the yarok-extended MJCF format (from MuJoCo). Then, you can include this component in the description of other components to build full robots or environments. At runtime, Yarok handles the nesting of components, etc.
| Controller        | Its the Python class that serves has the common interface for the component in all environments, and can access the controllers of its children components, that are nested in its .xml. Yarok autonomously instantiates and links parent-child controllers. |
| Interface         | MuJoCo (interface_mjc) or Real Hardware (interface_hw) interface. It serves as a proxy between the controller and the environment. Before instantiating the component **Controller**, Yarok merges the appropriate environment interface with the controller class, effectively becoming one. Thus, the controller should declare the interface(s) common public methods (api) as empty/pass.

##### Model description, using the Yarok-extended MJCF

All paths for meshes are relative to the component directory.

To nest a component onto its parent, the following macro can be used as an MJCF body element

| Name   | Description  |
|---|---|
| *tag name*    | The name of the component class. Same as the .xml and .py filenames.
| @name         | The name/id of the component instance.
| @parent       | When sub-nesting (check example) declares the name of the parent's link where to nest into.

Here we describe the extensions on top of the MJCF language, for the full documentation of MJCF check the [MuJoCo XML reference](https://mujoco.readthedocs.io/en/latest/XMLreference.html).

An **example** component  would look like:

../example/example.xml
```
``
../example/example.py

### The controller 

```
@component(
    components=[
        UR5,
        robotiq_2f85,
        gelsight2014,
        geltip,
        AnetA30,
        Cam
    ],
    interface_mjc=EmptyWorldInterfaceMJC
)
``





You can run the environment using the Yarok cli and/or programmatically.
Cli. 
###### Programmatic Yarok API

| Name   | Description  |
|---|---|
| load   | Loads the environment, instantiates components and links parent-child controllers|
| run    | Same as load, but runs the environment infinitly with a "while true, pass" loop |

###### CLI Yarok API
```
``` 

### Creating simple RL environment
Depending on the application, we have 3 suggestions 

* write an environment component that simply represents the "hardware" and have the control logic in your experimental script
* write a dedicated RL environment, 
* or even just extend our RL boilerplate class (RLBase). 

Here, the control logic in the main script
```
platform, manager = yarok.load(Env, ...)
ur5 = manager.get('ur5')

while True:
    st = [ur5.z]
    
    r = reward(st)
    
    a = ...
    ur5.move(a)
    
    platform.step()
    
```

Here, a parameterized component is written to hold the reward function (task definition), observation vector, etc.
The RL algorithm still goes in the main script.
```
@Component({
    UR5
})
class TaskEnv:
    
    def __init__(self, task, ur5):
           self.task = task
           self.ur5 = ur5      
  
    def state(self):
        """ Return the state representation
        return [ur5.xyz]
        
    def reward(self):
        if self.task == 'the_task':
            return ... your reward fn ...


platform, manager = yarok.load(RLEnv, {
    ...
    task: 'the_task'
})
ur5 = manager.get(TaskEnv)


while True:
       
    r = reward(st)
    
    a = ...
    ur5.move(a)
    
    platform.step()
    
```