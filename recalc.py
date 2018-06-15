import numpy as np
import time
from itertools import product
from matplotlib import pyplot as plt
from scipy.optimize import least_squares

pts = np.load('u:/repo/nrriboids/boids.np.array.npy')

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
for b in range(10):
    plt.plot(pts[:, b, 0], pts[:, b, 1])
plt.scatter(recvs[:, 0], recvs[:, 1])
plt.show()
for b in range(10):
    plt.plot(pts[:, b, 0], pts[:, b, 2])
plt.scatter(recvs[:, 0], recvs[:, 2])
plt.show()

# use center of all data as initial guess for position
start = np.array(((minx+maxx)/2, (miny+maxy)/2, (minz+maxz)/2))

begin = time.time()
for itr, brd in product(range(1000), range(10)):
    pos = pts[itr, brd]
    seps = pos - recvs
    def offby(x, seps=seps):
        return np.reshape(seps - (x - recvs), seps.size)
    calc = least_squares(offby, start)
    # print(pos, calc.x)
    # break
print("%d points in %f seconds, %f pts/sec" % (
    1000*10, time.time()-begin, 1000*10/(time.time()-begin)
))

