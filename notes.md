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

