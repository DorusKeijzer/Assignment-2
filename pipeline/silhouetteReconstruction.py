# loop over voxels v
	# loop over views c 
	# 	x = project(v)
	# 	store(c,x,v)

def lookuptable(voxels, views):
    for voxel in voxels:
        for view in views:
            image = project(voxel)
                