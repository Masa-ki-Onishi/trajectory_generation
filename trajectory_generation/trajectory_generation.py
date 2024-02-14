import rclpy  # ROS2のPythonモジュール
from rclpy.node import Node
from trajectory_generation.prompt import MAIN_PROMPT
import numpy as np
import math
import time
from rclpy.duration import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

import openai

l1 = 0.077
l2 = 0.13
l3 = 0.124
l4 = 0.126

class Task(Node):
    def __init__(self):
        super().__init__('PD3_mani') 

        #gptAPIキーを設定する
        openai.api_key = "<gptAPIキーを入力してください>"


        self.joint_pub = self.create_publisher(JointTrajectory, 'joint_trajectory_controller/joint_trajectory', 10)
        # Subscriber
        #self.create_subscription()
        # Value
        self.wrist_param = 30

        #実際に入力する角度
        self.joint_angle_list = []

        #gripperを最初から開いた状態にしておく
        self.gripper = -40

        #角度
        self.angle = []

        #座標
        self.position = []

        self.gripper_close = False
        self.joint_names = [
                'joint1',
                'joint2',
                'joint3',
                'joint4',
                'gripper'
                ]


    def publish_joint(self, joint_angle, execute_time=2):
        #ljoint_angle[3] += self.wrist_param
        # deg => rad
        joint_angle = list(map(math.radians, joint_angle))
        # メッセージの作成
        msg = JointTrajectory()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.joint_names = self.joint_names
        msg.points = [JointTrajectoryPoint()]
        msg.points[0].positions = list(map(float, joint_angle))
        msg.points[0].time_from_start = Duration(
                seconds=int(execute_time), nanoseconds=(execute_time-int(execute_time))*1e9).to_msg()
        # パブリッシュ
        self.get_logger().info('Publish joint.')
        self.joint_pub.publish(msg)
        time.sleep(execute_time + 0.5)
    

    def forward_kinematics(self, angle1, angle2, angle3, angle4):
        #角度[angle1, angle2, angele3, angle4, gripper]を入力する
        #座標[x, y, z]を返す

        print(f"###########################################")        
        angle22 = (90 - 10.6196) - angle2
        angle32 = (-90 + 10.6196) + (-angle3)
        angle44 = (-angle4)
        self.joint_angle_list = [angle1, angle22, angle32, angle44, self.gripper]
        self.publish_joint(self.joint_angle_list)

        px1 = round(l2*(np.cos(np.radians(angle2))) + l3*(np.cos(np.radians(angle2+angle3))) + l4*(np.cos(np.radians(angle2+angle3+angle4))), 6)
        pz1 = l2*(np.sin(np.radians(angle2))) + l3*(np.sin(np.radians(angle2+angle3))) + l4*(np.sin(np.radians(angle2+angle3+angle4))) + l1

        px = px1*(np.cos(np.radians(angle1)))
        py = px1*(np.sin(np.radians(angle1)))

        self.position = [px, py, pz1]
        self.angle = [angle1, angle2, angle3, angle4]
        print(f"position:{self.position}")
        print(f"angle:{self.angle}")
        print(f"###########################################")


    def inverse_kinematics(self, px, py, pz, pp):
        #座標[x, y, z]を入力する
        #角度[angle1, angle2, angele3, angle4, gripper]を返す


        print(f"###########################################")
        if pp > 180:
            pp = 180 - pp
        print(f"pp:{pp}")

        h = pz - (l1 + l4 * np.sin(np.radians(pp)))
        print(f"h:{h}")

        k1 = np.hypot(px, py)
        k2 = round(l4 * np.cos(np.radians(pp)), 6)
        print(f"k1:{k1} k2:{k2}")
        k = np.hypot(px, py) - round(l4 * np.cos(np.radians(pp)), 6)
        print(f"k:{k}")

        v = np.hypot(h, k)
        print(f"v:{v}")

        q = np.degrees(np.arctan(h / k))
        print(f"q:{q}")

        a = np.degrees(np.arccos((l2**2 + v**2 -l3**2)/(2 * l2 * v)))
        print(f"a:{a}")

        b1 = (l2**2 + l3**2 - v**2)
        b2 = (2 * l2 * l3)
        print(f"b1:{b1} b2:{b2}")
        bb = round((b1 / b2), 6)
        b = np.degrees(np.arccos((l2**2 + l3**2 - v**2)/(2 * l2 * l3)))
        if bb == 1 or bb == -1 :
            b = 180
        print(f"b:{b}")

        
        if px == 0 :
            if py > 0 :
                a1 = 90
            elif py < 0:
                a1 = -90
            else:
                a1 = 0
        else:
            a1 = np.degrees(np.arctan(py / px))

        if k < 0 :
            q = 180 + q
        a2 = a + q

        a3 = -180 + b
        a4 = pp - (a2 + a3)
        print(f"a1:{a1} a2:{a2} a3:{a3} a4:{a4}")
        
        a22 = (90 - 10.6196) - a2
        a32 = (-90 + 10.6196) + (-a3)
        a44 = (-a4)
        
        self.joint_angle_list = [a1, a22, a32, a44, self.gripper]
        self.publish_joint(self.joint_angle_list)

        self.position = [px, py, pz]
        self.angle = [a1, a2, a3, a4]
        print(f"position:{self.position}")
        print(f"angle:{self.angle}")
        print(f"###########################################")




    def open_manipulater(self):
        #何も返さない
        print(f"###########################################")
        self.gripper = -40
        self.joint_angle_list[4] = self.gripper
        self.publish_joint(self.joint_angle_list, 2)
        print(f"open gripper")
        print(f"###########################################")


    def close_manipulater(self):
        #何も返さない
        print(f"###########################################")
        self.gripper = 10
        self.joint_angle_list[4] = self.gripper
        self.publish_joint(self.joint_angle_list, 2)
        print(f"close gripper")
        print(f"###########################################")


    def task_completed(self):
        print(f"task completed")


    def get_chatgpt_output(self, model, new_prompt, messages, role):
        print(role + ":")
        print(new_prompt)
        messages.append({"role": role, "content": new_prompt})
        print(messages)

        completion = openai.ChatCompletion.create(
            model=model,
            temperature=0,
            messages=messages
        )
        
        print(completion)

        print("assistant:")


        new_output = ""

        content = completion['choices'][0]['message']['content']
        reason = completion['choices'][0]['finish_reason']

        if content is not None:
            print(content, end="")
            new_output += content
        else:
            print("finish_reason:", reason)

        messages.append({"role": "assistant", "content": new_output})


        return messages


    def code_split(self):

        #出力させるためのやつ
        forward_kinematics = self.forward_kinematics
        inverse_kinematics = self.inverse_kinematics
        open_manipulater = self.open_manipulater
        close_manipulater = self.close_manipulater
        task_completed = self.task_completed


        command = input("Enter a command: ")
        #api.command = command

        self.messages = []

        error = False

        new_prompt = MAIN_PROMPT.replace("[INSERT EE POSITION]", str(self.position)).replace("[INSERT TASK]", command).replace("[INSERT EE ANGLE]", str(self.angle))

        model = 'gpt-4'
        self.messages = self.get_chatgpt_output(model, new_prompt, self.messages, "system")
        
        if len(self.messages[-1]["content"].split("```python")) > 1:

                code_block = self.messages[-1]["content"].split("```python")

                block_number = 0
                
                for block in code_block:
                        if len(block.split("```")) > 1:
                            code = block.split("```")[0]
                            block_number += 1
                            print(code)
                            exec(code)

                 
 


def main():
    rclpy.init()
    node = Task()

    #node.inverse_kinematics(0.161, 0.135, 0.313, 90)
    #time.sleep(0.8)
    #node.close_manipulater()
    #time.sleep(0.8)
    node.forward_kinematics(0, 150, -150, 90)
    time.sleep(0.8)
    node.open_manipulater()
    node.code_split()

    node.destroy_node()
    rclpy.shutdown()

