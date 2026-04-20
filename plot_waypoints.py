import numpy as np
import matplotlib.pyplot as plt

wps = np.loadtxt(r"C:\Users\16222\Desktop\usv-path-planning\covplan_waypoints.txt")

if wps.ndim == 1:
    wps = wps.reshape(1, -1)

plt.figure()
plt.plot(wps[:, 1], wps[:, 0], 'o-', label='CovPlan waypoints')
plt.xlabel("East (m)")
plt.ylabel("North (m)")
plt.title("Exported CovPlan waypoints")
plt.grid(True)
plt.axis("equal")
plt.legend()

# 自动保存图片
plt.savefig(r"C:\Users\16222\Desktop\usv-path-planning\covplan_waypoints_plot.png", dpi=300, bbox_inches="tight")

plt.show()