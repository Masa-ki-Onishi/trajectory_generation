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


GPT-4のAPIキーを取得し、main.pyに入力する。
```main.py
class Task(Node):
    def __init__(self):
        super().__init__('PD3_mani') 

        #gptAPIキーを設定する
        openai.api_key = "<gptAPIキー>"
```

# 使用方法
- Terminal1
```
ros2 launch open_manipulator_description open_manipulator_x.launch.py
```

- Terminal2
```
ros2 run trajectory_generation trajectory_generation
```
Enter a command:\
に対して指示文を入力する。
