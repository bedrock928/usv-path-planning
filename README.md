# USV Coverage Path Planning Based on CovPlan

## 项目简介
本项目基于开源库 **CovPlan** 和 **PythonVehicleSimulator**，完成了无人船（USV）覆盖路径规划与船模轨迹跟踪的初步联调。

项目实现了从：
- 区域输入
- 覆盖路径生成
- 路径点导出
- 局部坐标转换
- Otter USV 跟踪仿真

的完整流程。

---

## 项目目标
本项目的主要目标包括：

1. 复现 CovPlan 的基础覆盖路径规划功能  
2. 将规划结果转换为船模可用的局部 North-East 航点  
3. 在 PythonVehicleSimulator 中驱动 Otter USV 对路径进行跟踪  
4. 分析联调过程中的控制效果与存在问题  

---

## 方法流程

### 1. 覆盖路径规划
使用 CovPlan 对给定区域进行覆盖路径规划，输入为经纬度多边形边界文件。

### 2. 航点导出
将 CovPlan 输出的经纬度路径点转换为局部 North-East 坐标，并保存为 `covplan_waypoints.txt`。

### 3. 船模跟踪
在 PythonVehicleSimulator 中调用 Otter USV 模型，基于简单航向参考更新策略进行路径跟踪。

---

## CovPlan 导出航点图
![CovPlan waypoints](covplan_waypoints_plot.png)

上图展示了由 CovPlan 输出并转换后的局部航点，整体呈现折返式覆盖路径特征。

---

## Otter USV 跟踪结果
![Otter tracking](otter_tracking_covplan_v1.png)

上图展示了 Otter USV 对 CovPlan 导出路径的第一版跟踪结果。

---

## 实验结果分析
实验表明，本项目已经成功完成了：

- CovPlan 覆盖路径生成  
- 路径点导出与坐标转换  
- Otter USV 船模读取航点并进行跟踪  

同时也发现当前系统仍存在以下问题：

- 拐点附近存在明显振荡  
- 航点较密时容易绕圈或过冲  
- 当前基于简单航向参考更新的控制策略仍较粗糙  

因此，本项目可以认为已经完成了路径规划与船模仿真的**初步闭环验证**，但在控制性能上仍有进一步优化空间。

---

## 运行方式

### 1. 生成 CovPlan 航点
```bash
python export_covplan_waypoints.py
###2. 查看航点图
python plot_waypoints.py
###3. 运行 Otter 跟踪仿真
python main.py

运行后选择：

3

即 Otter unmanned surface vehicle (USV)

###项目结构
usv-path-planning/
├── covplan_area.txt
├── covplan_waypoints.txt
├── export_covplan_waypoints.py
├── plot_waypoints.py
├── covplan_waypoints_plot.png
├── otter_tracking_covplan_v1.png
├── README.md
###当前结论

本项目已经成功完成 CovPlan 与 Otter USV 的第一版联调，实现了从覆盖路径规划到船模跟踪仿真的初步验证。

###后续优化方向

后续可以继续从以下几个方向优化：

使用 LOS guidance 或 Pure Pursuit 替代简单航向切换策略
对航点进行平滑处理，减少拐点振荡
引入障碍物场景与更复杂区域
比较不同路径规划算法与跟踪控制方法的效果
项目性质说明

###本项目属于“开源项目复现 + 船模联调实验”的初步研究工作。
重点在于完成路径规划与船模跟踪之间的联通，并分析联调过程中的问题与改进方向。
