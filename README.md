# trajectory_generation
# 環境

**hard**
- OpenManipulaterX
- U2D2

**soft**
- ubuntu 22.04
- ROS2 humble

# 準備
dynamixel_hardwareのセットアップ
```
cd ~/<workspace>
git clone -b humble https://github.com/youtalk/dynamixel_control.git
vcs import src < src/dynamixel_control/dynamixel_control.repos
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
. install/setup.bash
```
参考サイト
[dynamixel_hardware](https://github.com/dynamixel-community/dynamixel_hardware/tree/humble)

# 使用方法

