# DIGIT Simulator

## Introduction

This is a DIGIT-modified version of [GelSight simulator](https://github.com/danfergo/gelsight_simulation) in MUJOCO.

## Requirements

We have tested the codes in Ubuntu 18.04, and the python libs we use are as following:

```
mujoco == 2.2.2;  
gym == 0.25.0;
numpy == 1.23.3;
scipy == 1.8.1;
```

## Usage

To test the env we build and show the offscreen render image, e.g.
`
python env_test.py
`

## Citating Our Paper

If you use our codes in your research, please cite:

```
@article{ZHAO2022104321,
title = {Skill generalization of tubular object manipulation with tactile sensing and Sim2Real learning},
journal = {Robotics and Autonomous Systems},
pages = {104321}, 
year = {2022},
issn = {0921-8890},
doi = {https://doi.org/10.1016/j.robot.2022.104321}.
}
```
