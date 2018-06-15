## Getting x, y, z from “distance” to multiple known points


Use [Blender](https://www.blender.org/) to generate a synthetic
data set of x,y,z positions for “birds”, see
[this video](https://www.youtube.com/watch?v=bsCFReO-z1A)

Extract x, y, z from Blender boids particles (in Blender
Python console)

```python
# select particle generator object in view
object = bpy.context.object
data = object.particle_systems[0].particles
import numpy as np
pts = np.zeros(1000, 10, 3)
for t in range(1000):
    bpy.context.scene.frame_set(t)
    for h in range(10):
        pts[t][h] = data[h].location
np.save('boids.np.array', pts)
```

[recalc.py](./recalc.py) takes this data, places some sensors in the
same coordinate space, calculates separation from each sensor for each
observation, then re-calculates the position of the observation based on
the separations.

recalc.py uses least squares to find a point that most closely gives the
separations seen in the data, using the centroid of the data as a
starting guess.

In [compare_precise.pdf](./compare_precise.pdf) this works perfectly for
x and y coords and almost perfectly for z coords, although a few are
mis-calculated. That could probably be avoided by telling the least
squares function to try harder.

In [compare_degraded.pdf](./compare_degraded.pdf) the resolution of the
separations from bird to tower are reduced to about 50 m, and some
random noise is added. The x,y answer is probably still usable for
associating birds with patches, but the z answer is useless. This is
just because the x,y data covers hundreds of meters, whereas the z data
only covers 5, so the relative error is much greater.

The least squared solution is not terribly fast, about 100 pings per
second on a desktop. 50 birds pinging once ever 5 seconds is only 10
pings per second, so speed is probably not an issue, although constant
number crunching will increase power consumption.  There are probably
much better (less general) solutions, e.g. see [Multilateration](https://en.wikipedia.org/wiki/Multilateration)

So the question is how precisely can we measure separation from pinger
to tower. If the towers share a common clock and report time of arrival
of the ping, they need to time ping arrivals in nano seconds, or at
least tens of nanoseconds. TODO: see if PyBoards support
[utime.ticks_cpu()](https://docs.micropython.org/en/latest/pyboard/library/utime.html#utime.ticks_cpu)
and what the resolution is. Microsecond timing gives a resolution of
about 300 m, much worse than the simluated 50 m resolution in
compare_degraded.pdf

[Multilateration](https://en.wikipedia.org/wiki/Multilateration) uses
signal phase shift to get precise timings, not sure if FunCube dongle
will allow us to do that.

The alternative way of measuring separation would be signal strength. If
(a) we can measure that, (b) we can compensate for non-linear change,
and (c) there's enough resolution / difference in strength between
towers, then that may avoid some of the issues with time based
separation measurements.

