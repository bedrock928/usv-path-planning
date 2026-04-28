import numpy as np
from scipy.spatial import cKDTree

# =========================
# 1. 文件路径
# =========================
ref_file = r"C:\Users\16222\Desktop\usv-path-planning\covplan_waypoints.txt"
sim_file = r"C:\Users\16222\Desktop\usv-path-planning\simData_otter.csv"

# 仿真步长（与你 main.py / mainLoop.py 一致）
dt = 0.02

# =========================
# 2. 读取数据
# =========================
ref = np.loadtxt(ref_file)
sim = np.loadtxt(sim_file, delimiter=",")

if ref.ndim == 1:
    ref = ref.reshape(1, -1)

if sim.ndim == 1:
    sim = sim.reshape(1, -1)

# =========================
# 3. 从 simData 中提取轨迹
# =========================
# 默认假设：
# eta = sim[:, 0:6]
# nu  = sim[:, 6:12]
#
# 其中：
# eta[:,0] = North
# eta[:,1] = East
# nu[:,0]  = surge velocity u
# nu[:,5]  = yaw rate r
#
# 如果你后面发现索引不对，再改这里即可
traj = sim[:, [0, 1]]   # North, East
u = sim[:, 6]           # surge velocity
r = sim[:, 11]          # yaw rate

# =========================
# 4. 基础函数
# =========================
def path_length(points):
    """路径长度"""
    if len(points) < 2:
        return 0.0
    seg = np.diff(points, axis=0)
    return np.sum(np.linalg.norm(seg, axis=1))

def turning_angles(points):
    """相邻线段转角（弧度）"""
    if len(points) < 3:
        return np.array([])

    v1 = points[1:-1] - points[:-2]
    v2 = points[2:] - points[1:-1]

    n1 = np.linalg.norm(v1, axis=1)
    n2 = np.linalg.norm(v2, axis=1)

    valid = (n1 > 1e-8) & (n2 > 1e-8)

    cosang = np.ones(len(v1))
    cosang[valid] = np.sum(v1[valid] * v2[valid], axis=1) / (n1[valid] * n2[valid])
    cosang = np.clip(cosang, -1.0, 1.0)

    return np.arccos(cosang)

def smoothness_metric(points):
    """
    平滑度指标：转角平方和
    越小表示越平滑
    """
    ang = turning_angles(points)
    if len(ang) == 0:
        return 0.0
    return np.sum(ang ** 2)

def curvature_change_metric(points):
    """
    最大曲率变化（简单近似）
    """
    ang = turning_angles(points)
    if len(points) < 3 or len(ang) == 0:
        return 0.0

    seg = np.linalg.norm(np.diff(points, axis=0), axis=1)
    ds = 0.5 * (seg[:-1] + seg[1:])
    kappa = ang / np.maximum(ds, 1e-6)

    if len(kappa) < 2:
        return 0.0

    return np.max(np.abs(np.diff(kappa)))

def tracking_error_metrics(reference, trajectory):
    """
    最近点近似跟踪误差
    """
    tree = cKDTree(reference)
    dist, _ = tree.query(trajectory)

    mean_err = np.mean(dist)
    rmse_err = np.sqrt(np.mean(dist ** 2))
    max_err = np.max(dist)

    return mean_err, rmse_err, max_err

def energy_proxy_metric(u, r, dt):
    """
    简单能耗代理指标：
    用 surge velocity 和 yaw rate 构造
    不是物理真实能耗，只用于对比
    """
    return dt * np.sum(u**2 + 0.5 * r**2)

# =========================
# 5. 计算指标
# =========================
ref_length = path_length(ref)
traj_length = path_length(traj)

ref_smoothness = smoothness_metric(ref)
traj_smoothness = smoothness_metric(traj)

ref_max_curv_change = curvature_change_metric(ref)
traj_max_curv_change = curvature_change_metric(traj)

mean_err, rmse_err, max_err = tracking_error_metrics(ref, traj)

energy_proxy = energy_proxy_metric(u, r, dt)

# =========================
# 6. 输出结果
# =========================
print("====================================")
print("      Reference Path Metrics")
print("====================================")
print(f"Reference path length          : {ref_length:.3f} m")
print(f"Reference smoothness           : {ref_smoothness:.6f}")
print(f"Reference max curvature change : {ref_max_curv_change:.6f}")

print("\n====================================")
print("      Tracking Trajectory Metrics")
print("====================================")
print(f"Tracked path length            : {traj_length:.3f} m")
print(f"Tracked smoothness             : {traj_smoothness:.6f}")
print(f"Tracked max curvature change   : {traj_max_curv_change:.6f}")

print("\n====================================")
print("           Tracking Error")
print("====================================")
print(f"Mean tracking error            : {mean_err:.3f} m")
print(f"RMSE tracking error            : {rmse_err:.3f} m")
print(f"Max tracking error             : {max_err:.3f} m")

print("\n====================================")
print("          Energy Proxy")
print("====================================")
print(f"Energy proxy                   : {energy_proxy:.6f}")

# =========================
# 7. 保存结果到 txt
# =========================
output_txt = r"C:\Users\16222\Desktop\usv-path-planning\metrics_result.txt"
with open(output_txt, "w", encoding="utf-8") as f:
    f.write("Reference Path Metrics\n")
    f.write(f"Reference path length          : {ref_length:.3f} m\n")
    f.write(f"Reference smoothness           : {ref_smoothness:.6f}\n")
    f.write(f"Reference max curvature change : {ref_max_curv_change:.6f}\n\n")

    f.write("Tracking Trajectory Metrics\n")
    f.write(f"Tracked path length            : {traj_length:.3f} m\n")
    f.write(f"Tracked smoothness             : {traj_smoothness:.6f}\n")
    f.write(f"Tracked max curvature change   : {traj_max_curv_change:.6f}\n\n")

    f.write("Tracking Error\n")
    f.write(f"Mean tracking error            : {mean_err:.3f} m\n")
    f.write(f"RMSE tracking error            : {rmse_err:.3f} m\n")
    f.write(f"Max tracking error             : {max_err:.3f} m\n\n")

    f.write("Energy Proxy\n")
    f.write(f"Energy proxy                   : {energy_proxy:.6f}\n")

print(f"\nResults saved to: {output_txt}")