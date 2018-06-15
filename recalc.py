import numpy as np
import time
from itertools import product
from matplotlib import pyplot as plt
from scipy.optimize import least_squares

pts = np.load('u:/repo/nrriboids/boids.np.array.npy')

# Blender Boids params limited range, so scale up
pts[:, :, 0:2] *= 150


# get bounds on simulated x, y, z
minx = pts[:, :, 0].min()
maxx = pts[:, :, 0].max()
miny = pts[:, :, 1].min()
maxy = pts[:, :, 1].max()
minz = pts[:, :, 2].min()
maxz = pts[:, :, 2].max()

# didn't check z in Blender, so shift everything up
if minz < 0:
    txt = "%s->%s" % (minz, maxz)
    pts[:, :, 2] -= 1.01*minz
    maxz -= 1.01*minz
    minz -= 1.01*minz
    print("%s => %s->%s" % (txt, minz, maxz))

# cols x rows receivers, alternating between height_base and
# height_base+height_offset to decrease ambiguity
cols = 3
rows = 2
height_base = 0.6 * maxz
height_offset = 0.2 * maxz

# space the receviers evenly across the data range
rowsep = (maxy-miny) / (rows+1)
colsep = (maxx-minx) / (cols+1)

zs = np.ones(rows*cols)*height_base

# add height_offset to heights in checkerboard pattern
alt_height = np.reshape(
    np.mgrid[0:cols,0:rows].sum(axis=0) % 2, rows*cols
).astype(bool)
zs[alt_height] += height_offset

# array of receiver x,y,z positions
recvs = np.array([
    np.repeat(minx+np.arange(cols)*colsep+colsep, rows),
    np.tile(miny+np.arange(rows)*rowsep+rowsep, cols),
    zs
]).transpose()

# plot plan and fron elevation views of birds and receivers
plt.figure(figsize=(10, 8))
ax = plt.subplot(2, 2, 1)
ax.set_aspect('equal')
plt.xlabel('W-E m')
plt.ylabel('S-N m')
plt.title('Plan view, actual positions')
for b in range(10):
    plt.plot(pts[:, b, 0], pts[:, b, 1], zorder=1)
plt.scatter(recvs[:, 0], recvs[:, 1], c='k', zorder=2)
plt.subplot(2, 2, 2)
plt.xlabel('W-E m')
plt.ylabel('Height m')
plt.title('Front elev. view, actual positions')
for b in range(10):
    plt.plot(pts[:, b, 0], pts[:, b, 2], zorder=1)
plt.scatter(recvs[:, 0], recvs[:, 2], c='k', zorder=2)

# use center of all data as initial guess for position
start = np.array(((minx+maxx)/2, (miny+maxy)/2, (minz+maxz)/2))

begin = time.time()
ans = np.zeros_like(pts)
for itr, brd in product(range(1000), range(10)):
    if itr%10 == 0 and brd == 0:
        print(itr)
    pos = pts[itr, brd]
    seps = np.sqrt(np.power(pos - recvs, 2).sum(axis=1))

    if 0:
        # degrade resolutions of seps to 25% of receiver spacing
        seps = (seps / (0.25*colsep)).astype(int) * 0.25*colsep
        # add random noise of 10% of receiver spacing
        seps += np.random.rand(rows*cols)*0.1*colsep - 0.05*colsep

    def offby(x, seps=seps):
        cur = np.sqrt(np.power(x - recvs, 2).sum(axis=1))
        return seps - cur

    ans[itr, brd] = least_squares(offby, start).x

print("%d points in %f seconds, %f pts/sec" % (
    1000*10, time.time()-begin, 1000*10/(time.time()-begin)
))

# plot plan and fron elevation views of birds and receivers
ax = plt.subplot(2, 2, 3)
ax.set_aspect('equal')
plt.xlabel('W-E m')
plt.ylabel('S-N m')
plt.title('Plan view, calc. from separations')
for b in range(10):
    plt.plot(ans[:, b, 0], ans[:, b, 1], zorder=1)
plt.scatter(recvs[:, 0], recvs[:, 1], c='k', zorder=2)
plt.subplot(2, 2, 4)
plt.xlabel('W-E m')
plt.ylabel('Height m')
plt.title('Front elev. view, calc. from separations')
for b in range(10):
    plt.plot(ans[:, b, 0], ans[:, b, 2], zorder=1)
plt.scatter(recvs[:, 0], recvs[:, 2], c='k', zorder=2)
plt.tight_layout()
plt.savefig("compare.pdf")

