import os
def print_frame_ranges(path):
	''' Print animated sequences in 'path' in the following format:
		'name: 1001-2000' if there are no gaps
		'name: 1001, 1003-1500, 1600-2000' if there are gaps

        the format for an animated sequence is name.####.ext e.g. /job/.../my_render_v001.1001.jpg

	This function detects multiple-named sequences within the same directory.

	This function follows these basic steps:

		1. Get the file list and sort
		2. Iterate through the files and generate a dict of lists (`imgseq`). The keys of of the dict are the sequence names; the value is a list of low-high list-pairs. It can be described like this:
		
			# imgseq = {
			# 	'render_v001': [
			# 		[low_frame_int, high_frame_int]
			# 	]
			# }

			Each time a frame skips more than 1 frame from the previous recorded frame, a new 'list-pair' is created and appended.

		3. Iterate through `imgseq` converting existing low-frame/high-frame values as formatted zfill'd ranges or single frames format into a list.

		4. Iterate through zfilled list and print into format.

	'''

	# Get files from path
	if os.path.exists(path) == False:
		raise ValueError('%s does not exist!' % path)
		
	
	fd = sorted([x for x in os.listdir(path) if os.path.isfile('%s/%s' % (path,x))])
	
	imgseq = {}
	imgpad = 4 # Fixed digit padding (can be determined by examining actual filename)
	
	for f in fd:
		s_f = f.split('.')
		bn = s_f[0]
		fr = s_f[1]
		
		# Check if fr is numeric string.
		# If not numeric string, not part of sequence.. continue
		if fr.isdigit() == False:
			continue

		i_fr = int(fr) # int of frame number
		# Assuming filename extensions are the same
		# ex = s_f[2]

		# Multiple basenames supported
		# If basename not yet encountered, init lists
		if (bn in imgseq) == False:
			rng = [i_fr, i_fr]
			imgseq[bn] = []
			imgseq[bn].append(rng)

		elif (bn in imgseq) == True:
			# If already registered
			
			lastfr = imgseq[bn][-1][1] # determine the last recorded frame
			diff = i_fr - lastfr # Find the difference
			
			if diff > 1:
				# If cur frame is higher by more than 1 frame then there's a skip
				rng = [i_fr, i_fr] # start a new range
				imgseq[bn].append(rng)
			else:
				# No skip, just modify high frame
				o_i_fr = imgseq[bn][-1][0]
				rng = [o_i_fr, i_fr] # modify high frame
				imgseq[bn][-1] = rng
	
	
	# Generate another list with zfill'd ranges
	rngs = {}
	for k,rnglist in imgseq.items():
		if k not in rngs:
			rngs[k] = []
		for v in rnglist:
			if v[0] == v[1]: # If single frame
				rs = str(v[0]).zfill(imgpad) 
			else:
				# If frame range
				min_v = str(v[0]).zfill(imgpad)
				max_v = str(v[1]).zfill(imgpad)
				rs = '-'.join([min_v, max_v])
			rngs[k].append(rs)

	
	# Finally join up the lists and print
	for k,v in rngs.items():
		fs = '%s: %s' % (k, ', '.join(v))
		print(fs)


p = 'R:/PROJECTS/CINESITE/3d/images'
print_frame_ranges(p)