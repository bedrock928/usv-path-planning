import numpy as np
import covplan
import utm

# 1) CovPlan 参数
input_file = r"C:\Users\16222\Desktop\usv-path-planning\covplan_area.txt"

# 这些参数先用保守设置，后面再调
num_hd = 0
width = 5
theta = 90
num_clusters = 1
radius = 2

# 2) 调用 CovPlan，返回的是一串 lat-lon 航点
op = covplan.pathplan(
    input_file,
    num_hd=num_hd,
    width=width,
    theta=theta,
    num_clusters=num_clusters,
    radius=radius,
    visualize=False
)

# 3) 转成 numpy 数组
op = np.array(op, dtype=float)

# 如果没有生成航点，直接报错
if op.size == 0:
    raise ValueError("CovPlan returned an empty path.")

# 4) 经纬度 -> 局部 North-East（小区域近似）
lat0, lon0 = op[0]

meters_per_deg_lat = 111320.0
meters_per_deg_lon = 111320.0 * np.cos(np.deg2rad(lat0))

north = (op[:, 0] - lat0) * meters_per_deg_lat
east = (op[:, 1] - lon0) * meters_per_deg_lon

raw_ne = np.column_stack((north, east))

# 去掉几乎重复的点
if len(raw_ne) > 1:
    diff = np.linalg.norm(np.diff(raw_ne, axis=0), axis=1)
    keep = np.hstack(([True], diff > 0.5))
    raw_ne = raw_ne[keep]

# 抽样，先保留更多细节
step = 3
waypoints = raw_ne[::step]

# 保证最后一个点保留
if len(waypoints) == 0 or not np.allclose(waypoints[-1], raw_ne[-1]):
    waypoints = np.vstack([waypoints, raw_ne[-1]])

print("First 10 raw CovPlan points:")
print(op[:10])

print("First 10 converted NE waypoints:")
print(waypoints[:10])
# 6) 保存成你主循环正在读取的文件
output_file = r"C:\Users\16222\Desktop\usv-path-planning\covplan_waypoints.txt"
np.savetxt(output_file, waypoints, fmt="%.3f")

print("CovPlan raw points:", len(op))
print("Saved simulator waypoints:", len(waypoints))
print("Output file:", output_file)