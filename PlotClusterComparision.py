#!/data/apps/enthought_python/2.7.3/bin/python

import time
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from sklearn import cluster
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler
from GetClimateZone import GetClimateZone


GCZ_map, classes = GetClimateZone()
test = GCZ_map.copy()

test = (test>15).astype(np.uint8)
a,b = np.where(test==1)
data = np.hstack([a.reshape(-1,1),b.reshape(-1,1)])

clustering_names = ['MiniBatchKMeans', 'Birch']

fig=plt.figure()
two_means = cluster.MiniBatchKMeans(init='k-means++', n_clusters=26, batch_size=100,
    n_init=100, max_no_improvement=10, verbose=0,
    random_state=0)

birch = cluster.Birch(threshold=30,n_clusters=26)

clustering_algorithms = [two_means, birch]
plot_num = 1
cmap = plt.cm.jet
for name, algorithm in zip(clustering_names, clustering_algorithms):
	# predict cluster memberships
	t0 = time.time()
	algorithm.fit(data)
	t1 = time.time()
	# plot
	plt.subplot(1,len(clustering_algorithms), plot_num)
	plt.title(name, size=18)
	test1 = GCZ_map.copy()
	test1 = (test1>15).astype(np.float32)
	a,b = np.where(test1 == 1.)
	if hasattr(algorithm, 'labels_'):
		L = algorithm.labels_
	test1[a,b] = L
	test1[test1==0.] = np.NaN
	plt.imshow(test1, cmap=cmap)
	if hasattr(algorithm, 'cluster_centers_'):
		centers = algorithm.cluster_centers_
		plt.plot(centers[:, 1], centers[:, 0], 'go')
	elif hasattr(algorithm, 'subcluster_centers_'):
		centers = algorithm.subcluster_centers_
		plt.plot(centers[:, 1], centers[:, 0], 'go')
	plt.xticks(())
	plt.yticks(())
	plt.text(.99, .01, ('%.2fs' % (t1 - t0)).lstrip('0'),
                 transform=plt.gca().transAxes, size=15,
                 horizontalalignment='right')
	plot_num += 1

fig.savefig('hoang.png')
