#!/opt/local/bin/python
import Tkinter, Tkconstants, tkFileDialog 
import ttk as ttk
import tkMessageBox
from weight_inverse_distance import *
from bezier_chain_constraints import *
from svg_parser import *


colors = ['green', 'gold', 'brown', 'coral', 'cyan', 'gray', 'cadet blue', 
	'lawn green', 'medium spring green', 'green yellow', 'lime green', 'yellow green',
	'forest green', 'olive drab', 'dark khaki', 'khaki', 'pale goldenrod', 
	'light yellow', 'yellow', 'gold', 'light goldenrod', 'goldenrod', 'dark goldenrod', 
	'indian red', 'saddle brown', 'sandy brown',
	'dark salmon', 'salmon']
	
class Window:
	canvas = None
	popup = None
	mode = None #indicator of one of the three modes.
	constraint = None #indicator of which constraint is being used.
	
	root = None
	selected = None 
	traceT, traceR, traceS = [], [], []
	transforms = {}
	all_vertices = None
	facets = None
	all_weights = None
	boundaries = None
	W_matrices = None
	
	'''
	Construct UI
	'''
	def __init__(self, parent):
	
		self.root = parent
		self.root.title('Bezier Deformation')
		mainWindow = ttk.Frame(parent)	
		self.init_UI(mainWindow)	
		mainWindow.grid()
		return
		
	def init_UI(self, parent):
	
		menubar = ttk.Frame(parent, relief=Tkinter.GROOVE, borderwidth=1, width=800, height=28)
		self.init_menubar(menubar)
		
		self.canvas = Tkinter.Canvas(parent, width=800, height=600, bd=2, cursor='pencil', 
						relief=Tkinter.SUNKEN)
		self.canvas.bind("<Button-1>", self.onclick_handler)
		self.canvas.bind("<Shift-B1-Motion>", self.on_shift_mouse_handler)
		self.canvas.bind("<Control-B1-Motion>", self.on_control_mouse_handler)
#		self.canvas.bind("<Double-Button-1>", self.on_double_click_handler)
		self.canvas.bind("<B1-Motion>", self.on_motion_handler)
		self.canvas.bind("<ButtonRelease-1>", self.onrelease_handler)
		self.canvas.grid()
		return	
	
	def init_menubar(self, menubar):
	
		menubar.grid_propagate(0)
		menubar.grid()
		
		#A menu in Tk is a combination of a Menubutton (the title of the
		#menu) and the Menu (what drops down when the Menubutton is pressed)
			
		mb_file = ttk.Menubutton(menubar, text='file')
		mb_file.grid(column=0, row=0, ipadx=20)
		mb_file.menu = Tkinter.Menu(mb_file)
		mb_file.menu.add_command(label='import', command=self.askopenfilename)
		mb_file.menu.add_command(label='save', command=self.askopenfilename)
		mb_file.menu.add_separator()	
		mb_file.menu.add_command(label='triangle', command=self.draw_mesh)
		mb_file.menu.add_separator()	
		mb_file.menu.add_command(label='close', command=self.exit)
		
		##################
		mb_edit = ttk.Menubutton(menubar, text='edit')
		mb_edit.grid(column=1, row=0, ipadx=20 )
		mb_edit.menu = Tkinter.Menu(mb_edit)
		
		def change_mode():
			mode = self.mode.get()	
			if mode == 0:
				self.canvas.config(cursor = 'pencil')
			elif mode == 1: 
				self.canvas.config(cursor = 'target')
			elif mode == 2:
				self.canvas.config(cursor = 'hand1')		
		self.mode = Tkinter.IntVar()	
		mb_edit.menu.add_radiobutton(label='add control point', variable=self.mode, 
									value=0, command=change_mode)
		mb_edit.menu.add_radiobutton(label='add handle', variable=self.mode, value=1, 
									command=change_mode)
		mb_edit.menu.add_radiobutton(label='edit handle', variable=self.mode, value=2, 
									command=change_mode)
												
		mb_edit.menu.add_separator()
		self.if_closed = Tkinter.BooleanVar()
		mb_edit.menu.add_checkbutton(label='Path closed', onvalue=True, offvalue=False, 
									variable=self.if_closed)
		self.if_closed.set(True)
		
# 		self.if_show_mesh = Tkinter.BooleanVar()
# 		self.if_show_mesh.set(False)
# 		def show_mesh():
# 			debugger()
# 			print 'What is wrong?'
# 			if self.all_vertices is None: return
# 			if self.if_show_mesh == True:
# 				vs = self.all_vertices
# 				for face in self.facets:
# 					self.canvas.create_line([vs[x] for x in face]+vs[face[0]], 
# 											tags='original_mesh')
# # 				self.redraw_handle_affected_mesh()
# 			else: 
# 				self.canvas.delete('original_mesh')
# 		mb_edit.menu.add_checkbutton(label='show mesh', onvalue=True, offvalue=False, 
# 									variable=self.if_show_mesh, command=show_mesh)
											
		mb_edit.menu.add_separator()
		def clear_canvas():
			self.canvas.delete('all')
			self.transforms.clear()		
		mb_edit.menu.add_command(label='clear canvas', command=clear_canvas)
		
		
		######### menu dealing with constrains 
		mb_cons = ttk.Menubutton(menubar, text='constrains')
		mb_cons.grid(column=2, row=0)
		mb_cons.menu = Tkinter.Menu(mb_cons)
		self.constraint = Tkinter.IntVar()
		
		def change_constrain():	
			if ( len( self.canvas.find_withtag( 'approximated_curve' ) ) != 0 ):
				self.redraw_approximated_bezier_curve()
		mb_cons.menu.add_radiobutton(label='No constrains', variable=self.constraint, 
									value=0, command=change_constrain)		
		mb_cons.menu.add_radiobutton(label='C^0', variable=self.constraint, value=1, 
									command=change_constrain)
		mb_cons.menu.add_radiobutton(label='C^1', variable=self.constraint, value=2, 
									command=change_constrain)
		mb_cons.menu.add_radiobutton(label='G^1', variable=self.constraint, value=3, 
									command=change_constrain)
		
		mb_help = ttk.Menubutton(menubar,text='help')
		mb_help.grid(column=3, row=0, padx=300, sticky=Tkinter.E)
		
		mb_file['menu'] = mb_file.menu
		mb_edit['menu'] = mb_edit.menu
		mb_cons['menu'] = mb_cons.menu
#		mb_help['menu'] = mb_help.menu
		return 
		
		
	def askopenfilename(self):

		'''
		Returns an opened file in read mode.
		This time the dialog just returns a filename and the file is opened by your own code.
		'''
		# define options for opening or saving a file
		self.file_opt = options = {}
		options['defaultextension'] = '.svg'
		options['filetypes'] = [('all files', '.*'), ('svg files', '.svg')]
		options['initialdir'] = os.getcwd()
		options['initialfile'] = 'test0.svg'
		options['parent'] = self.root
		options['title'] = 'This is a title'
		
		# get filename
		filename = tkFileDialog.askopenfilename(**self.file_opt)
	
		sizes, pts = parse_svgfile(filename)
		
		self.canvas.config(width=sizes[0], height=sizes[1])

	def exit(self):
		sys.exit(0)
		
		
	def popup_handle_editor(self, handle_id):
	
		self.canvas.delete('popup') 
		self.selected = handle_id
		
		coord = self.canvas.bbox(handle_id)
		data = self.transforms[handle_id]
		values = []
		for i in range(0, 9):
			values.append(Tkinter.StringVar())
			values[i].set(data[i])
		
		frame = Tkinter.Frame(self.root, borderwidth=1, relief=Tkinter.RIDGE)
		labelFrame = Tkinter.LabelFrame(frame, text='Transform', relief=Tkinter.GROOVE, 
					borderwidth=1)
		labelFrame.grid()
		w11 = Tkinter.Entry(labelFrame, cursor='xterm', highlightcolor='cyan', width=6, 
					textvariable=values[0])
		w11.grid(row=0, column=0)
		w12 = Tkinter.Entry(labelFrame, cursor='xterm', highlightcolor='cyan', width=6, 
					textvariable=values[1])
		w12.grid(row=0, column=1)
		w13 = Tkinter.Entry(labelFrame, cursor='xterm', highlightcolor='cyan', width=6, 
					textvariable=values[2])
		w13.grid(row=0, column=2)
		w21 = Tkinter.Entry(labelFrame, cursor='xterm', highlightcolor='cyan', width=6, 
					textvariable=values[3])
		w21.grid(row=1, column=0)
		w22 = Tkinter.Entry(labelFrame, cursor='xterm', highlightcolor='cyan', width=6, 
					textvariable=values[4])
		w22.grid(row=1, column=1)
		w23 = Tkinter.Entry(labelFrame, cursor='xterm', highlightcolor='cyan', width=6, 
					textvariable=values[5])
		w23.grid(row=1, column=2)
		w31 = Tkinter.Entry(labelFrame, cursor='xterm', highlightcolor='cyan', width=6, 
					textvariable=values[6])
		w31.grid(row=2, column=0)
		w32 = Tkinter.Entry(labelFrame, cursor='xterm', highlightcolor='cyan', width=6, 
					textvariable=values[7])
		w32.grid(row=2, column=1)
		w33 = Tkinter.Entry(labelFrame, cursor='xterm', highlightcolor='cyan', width=6, 
					textvariable=values[8])
		w33.grid(row=2, column=2)
		
		popup = self.canvas.create_window((coord[0]+coord[2])/2, (coord[1]+coord[3])/2, 
				anchor=Tkinter.NW, width=204, height=140, window=frame, tags='popup')	
		
		def remove_popup(popup):	
			self.canvas.delete(popup)
		btn3 = Tkinter.Button(frame, text='Cancel', command=lambda popup=popup : 
				remove_popup(popup), width=4)
		btn3.grid(row=3, column=0, sticky=Tkinter.SE)
				
		def save_transforms(id, vals, popup):		
			for i in range(0, 9):
				self.transforms[id][i] = vals[i].get()
			remove_popup(popup)
		
			if len( self.canvas.find_withtag('controls') ) >= 4:
				self.redraw_handle_affected_curve()
				self.redraw_approximated_bezier_curve()	
			
		btn1 = Tkinter.Button(frame, text='Save', command=lambda id=handle_id, vals=values, 
				popup=popup : save_transforms(id, vals, popup), width=4)
		btn1.grid(row=3, column=0, sticky=Tkinter.SW)
		
		def delete_handle(id, popup):	
			self.canvas.delete(id)
			remove_popup(popup)
		
			if len( self.canvas.find_withtag('controls') ) >= 4:
				self.redraw_handle_affected_curve()
				self.redraw_approximated_bezier_curve()	
		btn2 = Tkinter.Button(frame, text='Delete', command=lambda id=handle_id, popup=popup : 
				delete_handle(id, popup), width=4)
		btn2.grid(row=3, column=0, sticky=Tkinter.S)
	
		self.popup = popup
		
	'''
	Construct UI ended
	'''
	'''
	A series of actions a user can do
	'''		
	def onclick_handler(self, event):
		
		mode = self.mode.get()
		if mode == 0:
			r= 3		 
			x0, x1, y0, y1 = event.x-r, event.x+r, event.y-r, event.y+r
			self.canvas.create_oval(x0, y0, x1, y1, fill='blue', outline='blue', 
									tags='controls')
					
		elif mode == 1:
			r = 3
			x0, x1, y0, y1 = event.x-r, event.x+r, event.y-r, event.y+r
			handle = self.canvas.create_rectangle(x0, y0, x1, y1, fill='red', outline='red', 
					tags='handles')
			self.transforms[handle] = identity(3).reshape(-1)
			self.popup_handle_editor( handle )
			if len( self.canvas.find_withtag('original_curve') ) > 0:
				self.redraw_handle_affected_curve()
				self.redraw_approximated_bezier_curve()
				
#				cps = self.get_controls()
#				handles = self.get_handle_pos()
#				update_precomputation_of_controls_or_handles(cps, handles)

		elif mode == 2:
			overlaps = self.canvas.find_overlapping(event.x-3, event.y-3, event.x+3, event.y+3)
			sels = set(overlaps) & set(self.canvas.find_withtag('handles')) 
			if len(sels) > 0:
				self.selected = sels.pop()
				self.popup_handle_editor(self.selected)

	# for translation ---- press and drag
	def on_motion_handler(self, event):
	
		if self.selected != None and self.popup != None: 
			h = self.selected
			if len(self.traceT) != 2:
				self.traceT = [event.x, event.y]
				return
				
			trans_x, trans_y = event.x-self.traceT[0], event.y-self.traceT[1]
			self.traceT = [event.x, event.y]
			
			window_name = self.canvas.itemcget( self.popup, 'window' )
			p = self.root.nametowidget( window_name )

			labelFrame = p.winfo_children()[0]
			entry_transX = labelFrame.winfo_children()[2]
			entry_transY = labelFrame.winfo_children()[5]
			
			ori_x, ori_y = self.transforms[h][2], self.transforms[h][5]
			new_x, new_y = trans_x+ori_x, trans_y+ori_y
			entry_transX.delete(0,Tkinter.END)
			entry_transX.insert(0,new_x)
			entry_transY.delete(0,Tkinter.END)
			entry_transY.insert(0,new_y)
			self.transforms[h][2], self.transforms[h][5] = new_x, new_y
			
#			self.canvas.move(self.selected, event.x-ori_x, event.y-ori_y)
			if len( self.canvas.find_withtag('affected_curve') ) > 0:
				self.redraw_handle_affected_curve()
				self.redraw_approximated_bezier_curve()				
		return
	
	# for rotation	---- Shift + press and drag
	def on_shift_mouse_handler(self, event):
	
		if self.selected != None and self.popup != None: 
			h = self.selected
			if len(self.traceR) != 2:
				coord = self.canvas.coords( h )
				self.traceR = [(coord[0]+coord[2])/2, (coord[1]+coord[3])/2]
				
			coord = self.canvas.coords( h )
			origin = [(coord[0]+coord[2])/2, (coord[1]+coord[3])/2]
			vec_0 = array([self.traceR[0]-origin[0], self.traceR[1]-origin[1]])
			vec_1 = array([event.x-origin[0], event.y-origin[1]])
			self.traceR = [event.x, event.y]
			
			assert len(vec_0) == len(vec_1)
			len_0 = sum([vec_0[i]**2 for i in range(len(vec_0))])**.5
			len_1 = sum([vec_1[i]**2 for i in range(len(vec_1))])**.5
			if len_0*len_1 == 0:
				return
			costheta = dot(vec_1, vec_0)/(len_0*len_1)
			sintheta = cross(vec_1, vec_0)/(len_0*len_1)
			
			window_name = self.canvas.itemcget( self.popup, 'window' )
			p = self.root.nametowidget( window_name )

			labelFrame = p.winfo_children()[0]
			entry_1 = labelFrame.winfo_children()[0]
			entry_2 = labelFrame.winfo_children()[1]
			entry_3 = labelFrame.winfo_children()[3]
			entry_4 = labelFrame.winfo_children()[4]
			
			entry_5 = labelFrame.winfo_children()[2]
			entry_6 = labelFrame.winfo_children()[5]
			
			R = array([[costheta, sintheta, 0], [-sintheta, costheta, 0], [0, 0, 1]])
			T = array([[1, 0, -origin[0]], [0, 1, -origin[1]], [0, 0, 1]])

			newM = dot((dot( dot(linalg.inv(T), R), T )), self.transforms[h].reshape(3, -1))
			self.transforms[h] = newM.reshape(-1)			
							
			entry_1.delete(0,Tkinter.END)
			entry_1.insert(0,newM[0][0])
			entry_2.delete(0,Tkinter.END)
			entry_2.insert(0,newM[0][1])
			entry_3.delete(0,Tkinter.END)
			entry_3.insert(0,newM[1][0])
			entry_4.delete(0,Tkinter.END)
			entry_4.insert(0,newM[1][1])
			entry_5.delete(0,Tkinter.END)
			entry_5.insert(0,newM[0][2])
			entry_6.delete(0,Tkinter.END)
			entry_6.insert(0,newM[1][2])
			
			if len( self.canvas.find_withtag('affected_curve') ) > 0:
				self.redraw_handle_affected_curve()
				self.redraw_approximated_bezier_curve()				
		return
	
	# for scaling ---- Control + press and drag
	def on_control_mouse_handler(self, event):
	
		if self.selected != None and self.popup != None:
			h = self.selected 
			if len(self.traceS) != 2:
				self.traceS = [event.x, event.y]
				return
				
			coord = self.canvas.coords( h )
			origin = [(coord[0]+coord[2])/2, (coord[1]+coord[3])/2]

			box = self.canvas.bbox('original_bezier')
			width, height = box[2]-box[0], box[3]-box[1]
			scaleX, scaleY = power(2., float(event.x-self.traceS[0])/width), power(2., 
							float(event.y-self.traceS[1])/height)
			
			self.traceS = [event.x, event.y]
			
			T = array([[1, 0, -origin[0]], [0, 1, -origin[1]], [0, 0, 1]])
			S = array([[scaleX, 0., 0.], [0., scaleY, 0.], [0., 0., 1.]])
			newM = dot(linalg.inv(T), dot(S, dot(T, self.transforms[h].reshape(3, -1) )))

			self.transforms[h] = newM.reshape(-1)

			
			window_name = self.canvas.itemcget( self.popup, 'window' )
			p = self.root.nametowidget( window_name )

			labelFrame = p.winfo_children()[0]
			entry_1 = labelFrame.winfo_children()[0]
			entry_2 = labelFrame.winfo_children()[1]
			entry_3 = labelFrame.winfo_children()[3]
			entry_4 = labelFrame.winfo_children()[4]
			
			entry_5 = labelFrame.winfo_children()[2]
			entry_6 = labelFrame.winfo_children()[5]
			entry_1.delete(0,Tkinter.END)
			entry_1.insert(0,newM[0][0])
			entry_2.delete(0,Tkinter.END)
			entry_2.insert(0,newM[0][1])
			entry_3.delete(0,Tkinter.END)
			entry_3.insert(0,newM[1][0])
			entry_4.delete(0,Tkinter.END)
			entry_4.insert(0,newM[1][1])
			entry_5.delete(0,Tkinter.END)
			entry_5.insert(0,newM[0][2])
			entry_6.delete(0,Tkinter.END)
			entry_6.insert(0,newM[1][2])
			
			if len( self.canvas.find_withtag('affected_curve') ) > 0:
				self.redraw_handle_affected_curve()
				self.redraw_approximated_bezier_curve()		
						
		return	
	
	def onrelease_handler(self, event):
	
		self.traceT = []
		self.traceR = []
		self.traceS = []
		
		if self.selected == None:
			self.canvas.delete('popup') 
		else:	
			self.selected = None

	'''
		Actions End
	'''
	'''
		algorithms for drawing
	'''	   
	# draw cubic bezier curve
	def draw_bezier_curve(self, cps):
		
		assert cps.shape == (4,3)
		known = asarray( M*cps ).reshape(4, -1)
		
		ps = [] 
		for t in range(0, 101):
			p = dot( asarray( [(float(t)/100)**3, (float(t)/100)**2, float(t)/100, 1] ), 
				known )
			ps = ps + [p[0], p[1]]	
		self.canvas.create_line(ps, width=2, tags='original_bezier')
	 
	def redraw_bezier_curve(self, cps):
	
		self.canvas.delete( 'original_bezier' )
		self.draw_bezier_curve( cps )
		
	# draw curve affected by the handles' weight
	def redraw_handle_affected_curve(self):
		
		if self.boundaries == None: return
		self.canvas.delete( 'affected_curve' )
		all_indices = self.boundaries
		w = self.all_weights
		vs = self.all_vertices
		
		for indices in all_indices:
			tps = []	
			for i in indices:
				m = zeros(9)
				p = asarray(vs[i] + [1.0])
				for j, h in enumerate(self.canvas.find_withtag('handles')):
					m = m + self.transforms[h]*w[i][j]
			
				p = dot( m.reshape(3, 3), p.reshape(3,-1) ).reshape(-1)
				tps = tps + [p[0], p[1]]

			self.canvas.create_line(tps, width=2, fill='magenta', tags='affected_curve')
			
# 	def redraw_handle_affected_mesh(self):
# 				
# 		self.canvas.delete( 'affected_mesh' )	
# 		all_pts = self.all_vertices
# 		
# 		tps = []
# 		w = self.all_weights
# 		for i, pts in enumerate(all_pts):
# 			p = asarray(pts + [1.])
# 			m = zeros(9)
# 			
# 			for j, h in enumerate(self.canvas.find_withtag('handles')):
# 				m = m + self.transforms[h]*w[i][j]
# 			
# 			p = dot( m.reshape(3, 3), p.reshape(3,-1) ).reshape(-1)
# 			tps.append([p[0], p[1]])
# 
# 		for face in self.facets:
# 			self.canvas.create_line([tps[x] for x in face]+tps[face[0]], fill='magenta', 
# 									tags='affected_mesh')
			
				
	def redraw_approximated_bezier_curve(self):
		
		level = self.constraint.get()
		self.canvas.delete( 'approximated_curve' )
		self.canvas.delete( 'new_controls' )
		
		handles = [item[1] for item in sorted(self.get_handles().items())]
		trans = [item[1] for item in sorted(self.transforms.items())]
		
		cps = self.get_controls()
		Cset = make_control_points_chain( cps, self.if_closed.get() )
		if Cset is None: return
		'''
		global gOnce
		
		import csv
		outname = 'integration_accuracy.csv'
		def uniquepath( path ):
			import os
			i = 1
			result = path
			while os.path.exists( result ):
				split = os.path.splitext( path )
				result = split[0] + ( ' %d' % i ) + split[1]
				i += 1
			return result
		
		writer = csv.writer( open( uniquepath( 'integration_accuracy.csv' ), 'w' ) )
		'''
		## for approximation of the partitions of a bezier curve.
		'''
		partition = [0.2, 0.4, 0.4]

		assert sum( partition ) == 1.0
		for x in partition:
			assert x > 0. and x <=1.
			
		P_primes = approximate_bezier_partitions( partition, cps, handles, trans, level)
		'''
		
		P_primes = approximate_beziers(self.W_matrices, Cset, handles, trans, level )

		# new control points
		for i in range( len( P_primes ) ):
			for pp in P_primes[i]:
				pp = asarray( pp ).reshape(3)
				r= 3
				x0, x1, y0, y1 = pp[0]-r, pp[0]+r, pp[1]-r, pp[1]+r
				self.canvas.create_oval(x0, y0, x1, y1, fill='green', outline='green', 
										tags='new_controls')

		num_sample = 100
		for i in range( len( P_primes ) ):
			known = asarray( M * P_primes[i] ).reshape(4, -1)	
			ps = [] 
			samples = array( range( num_sample ) ) / float(num_sample - 1)
			
			for t in samples:
				p = dot( asarray( [t**3, t**2, t, 1] ), known )
				ps = ps + [p[0], p[1]]	
			self.canvas.create_line(ps, smooth=True, width=2, fill='green', 
									tags='approximated_curve')

	'''
		Drawing End
	''' 
		
	
	## calculate the handles points on the canvas	 
	def get_handles(self):
		
		handles = {}
		H_set = self.canvas.find_withtag('handles')
		for h in H_set:
			pos = self.canvas.coords( h )
			pos = [(pos[0]+pos[2])/2, (pos[1]+pos[3])/2, 1.]
			handles[h] = pos
		
		return handles
	
	## calculate the control points on the canvas
	def get_controls(self):
	
		cps = self.canvas.find_withtag('controls')
		cps = [self.canvas.bbox(x) for x in cps]
		cps = [((x[0]+x[2])/2, (x[1]+x[3])/2, 1) for x in cps]
		cps = asarray(cps)
		
		return cps
		
	## sample all the original bezier curves on canvas, 
	## and tessellate with these sampled points.
	def draw_mesh(self):
		
		curves = self.canvas.find_withtag('original_bezier')
		cps = self.get_controls()
		Cset = make_control_points_chain( cps, self.if_closed.get() )
		if (Cset == None): return

		skeleton_handle_vertices = [item[1] for item in sorted(self.get_handles().items())]
		all_pts = sample_cubic_bezier_curve_chain( Cset )
		from itertools import chain
		loop = list( chain( *[ samples for samples, ts in asarray(all_pts)[:,:,:-1] ] ) )

		self.all_vertices, self.facets, self.all_weights = (triangulate_and_compute_weights
														(loop, skeleton_handle_vertices))
														
		## draw boundary bezier curves
		for pts, ts in all_pts:
			pts = pts[:,:-1].reshape(-1).tolist()
			self.canvas.create_line(pts, width=2, tags='original_bezier')

		## boundaries is a table of all the indices of the points on the boundary 
		## in all_vertices
		self.boundaries = [range(len(pts)) for pts, ts in all_pts]
		last = 0
		for i in range(len(self.boundaries)):
			self.boundaries[i] = asarray(self.boundaries[i])+last
			last = self.boundaries[i][-1]
		self.boundaries[-1][-1] = self.boundaries[0][0]	
		
		self.W_matrices = zeros( ( len( Cset ), len( skeleton_handle_vertices ), 4, 4 ) )
		for k in xrange(len( Cset )):
			for i in xrange(len( skeleton_handle_vertices )):
				self.W_matrices[k,i] = precompute_W_i_bbw( self.all_vertices, 
										self.all_weights, i, all_pts[k][0], all_pts[k][1])
			
		self.redraw_handle_affected_curve()	
 		self.redraw_approximated_bezier_curve()		
		
def main():
  
	root = Tkinter.Tk()
	app = Window(root)
	root.mainloop()	 

if __name__ == '__main__': main()
