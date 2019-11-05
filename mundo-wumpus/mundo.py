import random
 
class JuegoWumpus(object):
 
 
	def __init__(self, nodos=[]):
 
		# Crea las cuevas arbitariamente dada una lista de nodos 
		if nodos:
			cueva = {}
			N = max([nodos[i][0] for i in range(len(nodos))])
			for i in range(N):
				existe = [nodo[1] for nodo in nodos if nodo[0] == i]
				cueva[i] = existe
 
		# Si los nodos no son especificados se jugara con con 20 cuevas
		else:
			cueva = {1: [2,3,4], 2: [1,5,6], 3: [1,7,8], 4: [1,9,10], 5:[2,9,11],
				6: [2,7,12], 7: [3,6,13], 8: [3,10,14], 9: [4,5,15], 10: [4,8,16], 
				11: [5,12,17], 12: [6,11,18], 13: [7,14,18], 14: [8,13,19], 
				15: [9,16,17], 16: [10,15,19], 17: [11,20,15], 18: [12,13,20], 
				19: [14,16,20], 20: [17,18,19]}
 
		self.cueva = cueva
 
		self.amenazas = {}
 
		self.fechas = 5
 
		self.dintaciaViajeFlecha = 5		# As in the original game. I don't like this choice:
											# a bow should not cover a whole cueva.
		self.posicionJugador = -1
 
 
	"""
	HELPER: These methods wrap processes that are useful or called often.
	"""
 
 
	def irCuartosSeguros(self):
		""" Retorna una lista de todos los numeros de los cuartos
        que no tiene amenazas.
		"""
		return list(set(self.cueva.keys()).difference(self.amenazas.keys()))
 
 
	def llenarCueva(self):
		""" Selecciona al jugador y las amenazas en cuartos diferentes 
		"""
		for amenaza in ['hueco', 'hueco', 'wumpus']:
			pos = random.choice(self.irCuartosSeguros())
			self.amenazas[pos] = amenaza
		self.posicionJugador = random.choice(self.irCuartosSeguros())
 
 
	def busquedaAnchuraBFS(self, source, objetivo, max_profundidad=5):
		""" The game board (whether custom or standard dodecahedron) is an undirected graph. 
			The rooms are the vertices and the tunnels are the nodos of this graph. To find 
			out whether a objetivo room can be reached from a source room using a given amount 
			of tunnels, one can do a breadth first busqueda on the underlying undirected graph.
 
			BFS works like this: start with the source vertex, maybe it is already the objetivo? 
			If not, then go a level deeper and find out, if one of the children (also called 
			successors) of the source vertex is the wanted objetivo. If not, then for each child, 
			go a level deeper and find out if one of the grand-children is the wanted objetivo. 
			If not, then for each grand-child go a level deeper and so on. 
 
			The following is a recursive implementation of BFS. You will not find any loops 
			(for, while). Instead you manage two lists. The first one ('pila') contains all 
			the vertices of the current profundidad-level (e.g. all grand children). The second 
			('visitado') contains all vertices that you already checked. Now there are three 
			possibilites: Either pila is empty, then all vertices have been checked unsuccessfully;
			or the objetivo vertex is a member of the pila, then you are happy; or the objetivo is 
			not a member of the pila, but there are still some vertices that you did not visit, 
			then you append to the pila, all successors of the members of the pila and the old 
			pila now belongs to the visitado vertices.
		"""
		# Set up some initial values.
		graph = self.cueva
		profundidad = 0
 
		def busqueda(pila, visitado, objetivo, profundidad):
			if pila == []:					# The whole graph was busquedaed, but objetivo was not found.
				return False, -1
			if objetivo in pila:
				return True, profundidad
			visitado = visitado + pila
			pila = list(set([graph[v][i] for v in pila for i in range(len(graph[v]))]).difference(visitado))
			profundidad += 1
			if profundidad > max_profundidad:			# objetivo is too far away from the source.
				return False, profundidad
			else:							# Visit all successors of vertices in the pila.
				return busqueda(pila, visitado, objetivo, profundidad)
 
		return busqueda([source], [], objetivo, profundidad)
 
 
	"""
	Entradas / Salidas: Interacciones entre el jugador y el juego.
	"""
 
 
	def mostrarAdvertencias(self, amenaza):
		""" Es llamada cuando el jugador ingresa a un nuevo cuarto. Muestra las advertencias de todos sus frentes adyacentes.
		"""
		if amenaza == 'hueco':
			print("Estas sintiendo una briza")
		elif amenaza == 'wumpus':
			print("Estas oliendo mas cerca")
 
 
	def obtenerEntradaJugador(self):
		""" 
Consulta de entrada hasta que se proporcione una entrada válida.
		"""
		while 1:								# Query the action.
 
			inpt = input("Disparo o Movimiento (D-M)? ")
			try:								# Ensure that the player choses a valid action (shoot or move)
				mode = str(inpt).lower()
				assert mode in ['d', 'm', 'q']
				break
			except (ValueError, AssertionError):
				print("Esta accion no es valida: ingrese 'D'para disparo o 'M' para moverse.")
 
		if mode == 'q':							# I added a 'quit-button' for convenience.
			return 'q', 0
 
		while 1:								# Query the objetivo of the action.
 
			inpt = input("Adonde ?")
			try:								# Ensure that the chosen objetivo is convertable to an integer.
				objetivo = int(inpt)
			except ValueError:
				print("Este no es un numero valido.")
				continue						# Restart the while loop, to get a valid integer as objetivo.
 
			if mode == 'm':
				try:							# When walking, the objetivo must be adjacent to the current room.
					assert objetivo in self.cueva[self.posicionJugador]
					break
				except AssertionError:
					print("No puedes caminar tan lejos. Por favor use uno de los túneles.")
 
			elif mode == 's':
				try:							# When shooting, the objetivo must be reachable within 5 tunnels.
					bfs = self.busquedaAnchuraBFS(self.posicionJugador, objetivo)
					assert bfs[0] == True
					break
				except AssertionError:
					if bfs[1] == -1: 			# The objetivo is outside cueva.
						print("No hay espacio con este número en la cueva. Tu flecha viaja al azar.")
						objetivo = random.choice(self.cueva.keys())
					if bfs[1] > self.dintaciaViajeFlecha:				# The objetivo is too far.
						print("Las fechas no son tan torcidas.")
 
		return mode, objetivo
 
 
	"""
	MAIn / logica de juego
	"""
 
 
	def ingresoCuarto(self, numeroCuarto):
		""" 
        controla el proceso de ingreso a un nuevo cuarto
		"""	
		print("Entrando al cuarto {}...".format(numeroCuarto))
		# Tal vez una amezada puede estar en el cuarto.	
		if self.amenazas.get(numeroCuarto) == 'wumpus':
			print("Wumpus te  ha comido.")
			return -1
		elif self.amenazas.get(numeroCuarto) == 'hueco':
			print("Tu has caido en un pozo.")
			return -1
 
		# El cuarto es seguro; recopilar información sobre habitaciones adyacentes
		for i in self.cueva[numeroCuarto]:
			self.mostrarAdvertencias(self.amenazas.get(i))
 
		# Solo si no sucede nada más, el jugador entra en la habitación de su elección.
		return numeroCuarto
 
 
	def disparoCuarto(self, numeroCuarto):
		""" 
        Controla el proceso para poder disparar en cuarto
		"""
		print("Disparando una flecha en la habitación {}...".format(numeroCuarto))
		# Dispara una flecha y mira si algo es golpeado por ella.
		self.fechas -= 1
		amenaza = self.amenazas.get(numeroCuarto)
		if amenaza in ['wumpus']:
			del self.amenazas[numeroCuarto]		
			if amenaza == 'wumpus':
				print("Hurra, mataste al wumpus!")
				return -1
		elif amenaza in ['hueco', None]:
			print("Tu flecha fue en vano")
 
		# Si esta fue tu última flecha y no alcanzó el wumpus ..
		if self.fechas < 1: # Esto (o la actualización de self.fechas) parece estar roto ..
			print("Tu carcaj esta Vacia")
			return -1
 
		#  If you shoot into another room, the Wumpus has a 75% of chance of waking up and moving into an adjacent room.
		if random.random() < 0.75:
			#print("DEBUG: Wumpus moved.")
			for numeroCuarto, amenaza in self.amenazas.items():
				if amenaza == 'wumpus':
					wumpus_pos = numeroCuarto					
			new_pos = random.choice(list(set(self.cueva[wumpus_pos]).difference(self.amenazas.keys())))
			del self.amenazas[numeroCuarto]
			self.amenazas[new_pos] = 'wumpus'			
			if new_pos == self.posicionJugador: # Wumpus entered players room.
				print("Wumpus ingreso a tu cuarto Game Over!")
				return -1
 
		return self.posicionJugador
 
 
	def cicloJuego(self):
 
		print("El mundo de wumpus")
		print("===============")
		print()
		self.llenarCueva()
		self.ingresoCuarto(self.posicionJugador)
 
		while 1:
 
			#print("DEBUG: Your quiver holds {} fechas.".format(self.fechas))			
			#print("DEBUG: Rooms with no amenazas are: {}.".format(self.irCuartosSeguros()))			
			#print("DEBUG: amenazas are located in the following rooms: {}".format(self.amenazas))
 
			print("Tu estas en el cuarto {}.".format(self.posicionJugador), end=" ")
			print("Los túneles conducen a:  {0}  {1}  {2}".format(*self.cueva[self.posicionJugador]))
 
 
			inpt = self.obtenerEntradaJugador()		# Player choses move or shoot.
			print()								# Visual separation of rounds.
			if inpt[0] == 'm':					# Move.
				objetivo = inpt[1] 
				self.posicionJugador = self.ingresoCuarto(objetivo)
			elif inpt[0] == 's':				# Shoot.
				objetivo = inpt[1]
				self.posicionJugador = self.disparoCuarto(objetivo)
			elif inpt[0] == 'q':				# Quit.
				self.posicionJugador = -1
 
			if self.posicionJugador == -1:			# E.g. Deadly amenaza, quiver empty, etc.
				break							# If any of the game loosing conditions are True,
												# then posicionJugador will be -1. 
 
		print()
		print("Game over!")	
 
 
if __name__ == '__main__':						
	# Only executed if you start this script as the main script,
	# i.e. you enter 'python path/to/wumpus.py' in a terminal.
	# Assuming you saved the script in the directory 'path/to' 
	# and named it 'wumpus.py'.
 
	# TODO: In the original game you can replay a dungeon (same positions of you and the amenazas)
 
	WG = JuegoWumpus()
	WG.cicloJuego()
 