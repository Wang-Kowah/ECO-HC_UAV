# ECO-HC on UAV
ECO with hand-crafted features on UAV

## Build demo
```bash
cd ECO-HC_UAV/eco/features/
python setup.py build_ext --inplace
```

## Usage
To run our demo on Airsim, install the requirements below
```bash
pip install numpy pandas scipy python-opencv pillow airsim
```
Then install [Unreal Engine 4](https://www.unrealengine.com/download) to run the simulation environment

Build an environment by youself or download from [released environments](https://github.com/microsoft/AirSim/releases)

Run the environment and choose no to use quadrotor simulation

Now you can run the demo and draw a box on target to start tracing
```bash
cd ECO-HC_UAV/
python demo_airsim.py
```

See [docs](https://github.com/microsoft/AirSim/tree/master/docs) and [PythonClient](https://github.com/microsoft/AirSim/tree/master/PythonClient) to learn more about Airsim's API

## Note
Python implementation of ECO by [pyECO](https://github.com/StrangerZhang/pyECO), using ResNet50 feature instead of the original imagenet-vgg-m-2048

Our demo only use ECO-HC for efficiency

## Reference
[1] Danelljan, Martin and Bhat, Goutam and Shahbaz Khan, Fahad and Felsberg, Michael.
​    ECO: Efficient Convolution Operators for Tracking
​    In Conference on Computer Vision and Pattern Recognition (CVPR), 2017
