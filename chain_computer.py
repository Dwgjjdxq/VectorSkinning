from copy import copy, deepcopy
from bezier_constraint_odd_solver import *
from bezier_constraint_even_solver import *


class Control_point:
	'''
	Class of control point.
	id is the control point's id.
	position is its relative position with respect to the canvas
	is_joint tells if it is an joint point. If so, it has constraint whose first element corresponds to one of the four types of C^0, fixed angle, C^1 and G^1, and second element indicates if its position is fixed.
	'''
	id = -1
	position = zeros(2)
	is_joint = False
	constraint = None
	
	def __init__(self, id, pos, is_joint=False, constraint = [1,0] ):
		pos = asarray( pos )
		constraint = asarray( constraint )
		assert len( pos ) == 2
		assert len( constraint ) == 2
	
		self.id = id
		self.position = pos
		self.is_joint = is_joint
		if is_joint:
			self.constraint = constraint
			
	def compare_shape( compared_control ):
		assert isinstance( compared_control, Handle )
		if compared_control.id == self.id and array_equal( compared_control.position, self.position) and compared_control.is_joint == self.is_joint and array_equal( compared_control.constraint, self.constraint ) :
			return True
		else: 
			return False

class Engine:
	'''
	A data persistant that have all information needed to precompute and the system matrix of the previous state.
	'''
	handle_positions = []
	transforms = []
	
	all_controls = []
	all_constraints = []
	boundary_index = 0
	
	precomputed_parameter_table = []
	is_ready = False
	
# 	def __init__( control_pos=None, handles=None ):
# 		if control_pos is not None:
# 			set_control_positions(control_pos)
# 			
# 		if handles is not None:
# 			setup_configuration( controls, handles )
# 			self.is_ready = True
	
	def set_control_positions( self, paths_info, boundary_index ):
		'''
		initialize the control points for multiple paths and make the default constraints
		boundary_index tells which path is the outside boundary
		'''
		self.boundary_index = boundary_index
		all_controls = [ make_control_points_chain( path[u'cubic_bezier_chain'], path[u'closed'] ) for path in paths_info]
		all_constraints = [ make_constraints_from_control_points( controls, path[u'closed'] ) for controls, path in zip( all_controls, paths_info ) ]
		
		self.all_controls = all_controls
		self.all_constraints = all_constraints		
			
	def constraint_change( self, path_index, joint_index, constraint ):
		'''
		change the constraint at a joint of a path.
		path_index tells which path, joint_index tells which joint
		'''
		constraint = asarray( constraint )
		assert constraint.shape == (2, )
		
		self.all_constraints[ path_index ][ joint_index ] = constraint

	def transform_change( self, i, transform ):
		'''
		change the transform at the index i
		'''
		assert i in range( len( self.transforms ) )
		transform = asarray( transform )
		if len( transform ) == 2:
			transform = concatenate( ( transform, array( [[0, 0, 1]] ) ), axis=0 )
		assert transform.shape == (3,3)
		
		self.transforms[i] = transform
	
	def set_handle_positions( self, handles ):
		'''
		set new handles with identity transforms and keep old handles and transforms unchanged.
		'''
		handles = asarray( handles )
		handle_positions = self.handle_positions
		handle_positions = asarray( handle_positions )
		num_adding = len( handles ) - len( handle_positions	)
		
		assert num_adding >= 0
		if len( handle_positions ) != 0:
			assert array_equal( handle_positions, handles[ :len( handle_positions ) ] )
		
		self.handle_positions = handles.tolist()
		
		for i in range( num_adding ):
			self.transforms.append( identity(3) )
		
	def solve( self ):
		raise NotImplementedError('Solve has not been done yet.')
		
def get_controls( controls ):
	'''
	given a list of Control_point classes, return each control point's position and the joint's constraint.
	'''
	control_pos = []
	constraints = []
	for control in controls:
		control_pos.append( control.position )
		if control.is_joint:
			assert control.constraint is not None
			constraints.append( control.constraint )
		
	control_pos = make_control_points_chain( control_pos )

	return asarray(control_pos), asarray(constraints)

## The dimensions of a point represented in the homogeneous coordinates
dim = 2
	
def approximate_beziers(W_matrices, controls, handles, transforms, all_weights, all_vertices, all_indices, all_pts, all_dts, enable_refinement=False):
	
	'''
	### 1 construct and solve the linear system for the odd iteration. if the constraints don't contain fixed angle and G1, skip ### 2.
	### 2 If the constraints contain any fixed angle and G1, iterate between the even and odd system until two consecutive solutions are close enough.
	### 3 compute the bbw curves
	### 4 compute all the points along the curves.
	### 5 refine the solutions based on the error of each curve. If it is larger than a threshold, split the curve into two.
	'''
	
	solutions = None
	control_pos, constraints = get_controls( controls )
	control_pos = concatenate((control_pos, ones((control_pos.shape[0],4,1))), axis=2)

	### 1
	odd = BezierConstraintSolverOdd(W_matrices, control_pos, constraints, transforms )
#	odd.update_rhs_for_handles( transforms )
	last_solutions = solutions = odd.solve()

	### 2	
	if 2 in constraints[:,0] or 4 in constraints[:,0]: 

		even = BezierConstraintSolverEven(W_matrices, control_pos, constraints, transforms )	
	#		even.update_rhs_for_handles( transforms )

		for iter in xrange( 1 ):
			even.update_system_with_result_of_previous_iteration( solutions )
			last_solutions = solutions
			solutions = even.solve()
		
			if allclose(last_solutions, solutions, atol=1.0, rtol=1e-03):
				break
		
			## Check if error is low enough and terminate
			odd.update_system_with_result_of_previous_iteration( solutions )
			last_solutions = solutions
			solutions = odd.solve()
		
			if allclose(last_solutions, solutions, atol=0.5, rtol=1e-03):
				break
					
	### 3 
	bbw_curves = []
	for indices in all_indices:
		tps = []	
		for i in indices:
			m = zeros(9)
			p = asarray(all_vertices[i] + [1.0])
			for h in range(len(transforms)):
				m = m + transforms[h]*all_weights[i,h]
		
			p = dot( m.reshape(3, 3), p.reshape(3,-1) ).reshape(-1)
			tps = tps + [p[0], p[1]]	
		bbw_curves.append(tps)
	
	### 4
	spline_skin_curves = []
	for k, solution in enumerate(solutions):
		tps = []
		for t in asarray(all_pts)[k, 1]:
			tbar = asarray([t**3, t**2, t, 1.])
			p = dot(tbar, asarray( M * solution ) )
			tps = tps + [p[0], p[1]]
		spline_skin_curves.append(tps)
	
	
	### 5
# 	new_controls = adapt_configuration_based_on_diffs( controls, bbw_curves, spline_skin_curves, all_dts )
# 	
# 	if enable_refinement and len( new_controls ) > len( controls ):	
# # 		debugger()
# 		new_control_pos = get_controls( new_controls )[0]
# 
# 		W_matrices, all_weights, all_vertices, all_indices, all_pts, all_dts = precompute_all_when_configuration_change( new_control_pos, handles  )
# 	
# 		solutions, bbw_curves, spline_skin_curves = approximate_beziers(W_matrices, new_controls, handles, transforms, all_weights, all_vertices, all_indices, all_pts, all_dts, False)	
	
	return solutions, bbw_curves, spline_skin_curves


def adapt_configuration_based_on_diffs( controls, bbw_curves, spline_skin_curves, all_dts ):
	'''
	 sample the bezier curve solution from optimization at the same "t" locations as bbw-affected curves. Find the squared distance between each corresponding point, multiply by the corresponding "dt", and sum that up. That's the energy. Then scale it by the arc length of each curve.
	'''
	assert len( bbw_curves ) == len( spline_skin_curves )
	diffs = [compute_error_metric(bbw_curve, spline_skine_curve, dts) for bbw_curve, spline_skine_curve, dts in zip(bbw_curves, spline_skin_curves, all_dts) ]
	print 'differences: ', diffs
	
	new_controls = []
	partition = [0.5, 0.5]
	threshold = 100 
	
	all_pos = asarray([x.position for x in controls])
	
	for k, diff in enumerate( diffs ):
		control_pos = all_pos[ k*3 : k*3+4 ]
		if len(control_pos) == 3:	
			control_pos = concatenate((control_pos, all_pos[0].reshape(1,2)))
		
		if diff > threshold*length_of_cubic_bezier_curve(control_pos):
			splitted = split_cublic_beizer_curve( control_pos, partition )
			splitted = asarray( splitted ).astype(int)
# 			debugger()
			
			new_controls.append( controls[ k*3 ] )
			for j, each in enumerate(splitted):
				new_controls += [ Control_point(-1, each[1], False), Control_point(-1, each[2], False) ]
				if j != len(splitted)-1:
					new_controls.append( Control_point(-1, each[-1], True, [4,0]) )	
			
		else:
			new_controls += [ controls[i] for i in range( k*3, k*3+3 ) ]
			
	'''
	if is not closed, add the last control at the end.
	'''
	
	return new_controls


def precompute_all_when_configuration_change( controls_on_boundary, all_control_positions, skeleton_handle_vertices  ):
	'''
	precompute everything when the configuration changes, in other words, when the number of control points and handles change.
	W_matrices is the table contains all integral result corresponding to each sample point on the boundaries.
	all_weights is an array of num_samples-by-num_handles
	all_vertices is an array of positions of all sampling points. It contains no duplicated points, and matches to all_weights one-on-one
	all_indices is an array of all indices in all_vertices of those sampling points on the boundaries(the curves we need to compute).
	all_pts is an array containing all sampling points and ts for each curve.(boundaries)
	all_dts contains all dts for each curve. It is in the shape of num_curve-by-(num_samples-1)
	'''
	num_samples = 100
	all_data = asarray([ [sample_cubic_bezier_curve_chain( control_pos, num_samples )] for control_pos in all_control_positions ])
	all_pts = all_data[:,0]
	all_dta = all_data[:,1]
	
	boundary_pts, boundary_dts = sample_cubic_bezier_curve_chain( controls_on_boundary, num_samples )
	
	all_vertices, facets, all_weights = triangulate_and_compute_weights( boundary_pts, skeleton_handle_vertices, all_pts )
	
	## all_indices is a table of all the indices of the points on all paths 
	## in all_vertices
	all_indices = [[range(len(pts)) for pts, ts in path] for path in all_pts]
	
	for path_indices in len( all_indices ):
		last = 0
		for i in range( len( path_indices ) ):
			path_indices[i] = asarray(path_indices[i])+last
			last = path_indices[i][-1]
		path_indices[-1][-1] = path_indices[0][0] 
		
	W_matrices = []
	for j, control_pos in enumerate( all_control_positions ):
		W_matrices.append( zeros( ( len( control_pos ), len( skeleton_handle_vertices ), 4, 4 ) ) )		
		for k in xrange(len( control_pos )):	
			for i in xrange(len( skeleton_handle_vertices )):
				## indices k, i, 0 is integral of w*tbar*tbar.T, used for C0, C1, G1,
				## indices k, i, 1 is integral of w*tbar*(M*tbar), used for G1
				W_matrices[k,i] = precompute_W_i_bbw( all_vertices, all_weights, i, all_pts[j,k,0], all_pts[j,k,1], all_dts[j,k])
				
	W_matrices = asarray( W_matrices )
			
	return [W_matrices, all_weights, all_vertices, all_indices, all_pts, all_dts]

	
		
def main():
	'''
	a console test.
	'''
	paths_info =  [
{u'bbox_area': 73283.73938483332,
  u'closed': True,
  u'cubic_bezier_chain': [[46.95399856567383, 114.95899963378906],
                          [35.944000244140625, 177.95700073242188],
                          [96.1259994506836, 266.40399169921875],
                          [198.39999389648438, 266.40399169921875],
                          [300.67401123046875, 266.40399169921875],
                          [342.614990234375, 182.7259979248047],
                          [342.614990234375, 122.19000244140625],
                          [342.614990234375, 61.65399932861328],
                          [366.375, 19.503999710083008],
                          [241.58200073242188, 21.156999588012695],
                          [116.78900146484375, 22.809999465942383],
                          [61.83000183105469, 29.834999084472656],
                          [46.95399856567383, 114.95899963378906]]},
#   {u'bbox_area': 55.29089948625202,
#   u'closed': False,
#   u'cubic_bezier_chain': [[-255.1510009765625, 5.1479997634887695],
#                           [-255.76300048828125, 9.116000175476074],
#                           [-263.0260009765625, 8.20199966430664],
#                           [-263.8190002441406, 5.1479997634887695],
#                           [-263.51300048828125, -0.24000000953674316],
#                           [-255.78399658203125, 0.5950000286102295],
#                           [-255.1510009765625, 5.1479997634887695],
#                           [-260.4859924316406, 5.1479997634887695],
#                           [-259.3039855957031, 4.995999813079834],
#                           [-257.14300537109375, 5.821000099182129],
#                           [-257.8190002441406, 3.815000057220459],
#                           [-259.3370056152344, 3.628000020980835],
#                           [-260.32598876953125, 3.9749999046325684],
#                           [-260.4859924316406, 5.1479997634887695]]},                        
#                           
#  {u'bbox_area': 4.065760665711228,
#   u'closed': True,
#   u'cubic_bezier_chain': [[155.34100341796875, 86.31900024414062],
#                           [156.80299377441406, 86.19999694824219],
#                           [157.47000122070312, 86.86699676513672],
#                           [157.34300231933594, 88.32099914550781],
#                           [157.34300231933594, 88.32099914550781],
#                           [155.34100341796875, 88.32099914550781],
#                           [155.34100341796875, 88.32099914550781],
#                           [155.34100341796875, 88.32099914550781],
#                           [155.34100341796875, 86.31900024414062],
#                           [155.34100341796875, 86.31900024414062]]},                          
#  {u'bbox_area': 6.86434952491282,
#   u'closed': False,
#   u'cubic_bezier_chain': [[-272.48699951171875, -4.85099983215332],
#                           [-270.177001953125, -5.317999839782715],
#                           [-270.0920104980469, -2.513000011444092],
#                           [-271.1549987792969, -1.5190000534057617],
#                           [-272.614990234375, -1.61899995803833],
#                           [-272.5870056152344, -3.197000026702881],
#                           [-272.48699951171875, -4.85099983215332]]}
					]
	
	skeleton_handle_vertices = [[176, 126]]	
# 	skeleton_handle_vertices = [[200.0, 300.0, 1.0], [300.0, 300.0, 1.0]] 
	
	constraint = [0, 3, (2,1) ]
	
	engine = Engine()
	boundary_path = max(paths_info, key=lambda e : e[u'bbox_area']) 
	boundary_index = paths_info.index( boundary_path )
	
	engine.set_control_positions( paths_info, boundary_index )
	
 	engine.constraint_change( constraint[0], constraint[1], constraint[2] )

	engine.set_handle_positions( skeleton_handle_vertices )
 	
# 	engine.set_transforms()
	
	debugger()
	parameters = precompute_all_when_configuration_change( control_pos, skeleton_handle_vertices  )
	
	trans = [array([ 1.,  0.,  0.,	0.,	 1.,  0.,  0.,	0.,	 1.]), array([ 1.,	0.,	 0.,  0.,  1., 0., 0., 0., 1.])]	  
						   

	
	P_primes, bbw_curves, spline_skin_curves = approximate_beziers(W_matrices, control_pos, skeleton_handle_vertices, trans, constraints, all_weights, all_vertices, all_indices, all_pts, all_dts )
	
	print 'HAHA ~ '
	print P_primes
	
if __name__ == '__main__': main()		
