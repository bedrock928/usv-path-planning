import numpy as np
import covplan
import utm

# 1) CovPlan 参数
input_file = r"C:\Users\16222\Desktop\usv-path-planning\covplan_area_real_small.txt"

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

# 缩放到适合小尺度船模仿真的范围
scale = 0.01
raw_ne = raw_ne * scale

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
def smooth_waypoints(wps, alpha=0.15, iters=3):
    out = wps.copy()
    for _ in range(iters):
        new = out.copy()
        new[1:-1] = (1 - 2 * alpha) * out[1:-1] + alpha * out[:-2] + alpha * out[2:]
        out = new
    return out
def truncate_by_length(wps, max_length=150.0):
    if len(wps) < 2:
        return wps

    out = [wps[0]]
    total = 0.0

    for i in range(1, len(wps)):
        seg_len = np.linalg.norm(wps[i] - wps[i - 1])

        if total + seg_len > max_length:
            break

        out.append(wps[i])
        total += seg_len

    return np.array(out)

output_file = r"C:\Users\16222\Desktop\usv-path-planning\covplan_waypoints.txt"
def downsample_by_distance(wps, min_dist=8.0, max_points=40):
    """
    航点稀疏化：
    1. 先按最小距离筛选航点
    2. 如果航点还是太多，再强制限制最大航点数
    """
    if len(wps) < 2:
        return wps

    # 第一步：按距离稀疏化
    out = [wps[0]]
    last = wps[0]

    for p in wps[1:]:
        if np.linalg.norm(p - last) >= min_dist:
            out.append(p)
            last = p

    if not np.allclose(out[-1], wps[-1]):
        out.append(wps[-1])

    out = np.array(out)

    # 第二步：如果点还是太多，强制抽样到 max_points 个以内
    if len(out) > max_points:
        idx = np.linspace(0, len(out) - 1, max_points).astype(int)
        out = out[idx]

    return out
waypoints = downsample_by_distance(waypoints, min_dist=12.0, max_points=12)
np.savetxt(output_file, waypoints, fmt="%.3f")
print("Saved simulator waypoints:", len(waypoints))
print("CovPlan raw points:", len(op))
print("Saved simulator waypoints:", len(waypoints))
print("Output file:",output_file)
