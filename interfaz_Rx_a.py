import pygame
import time
import os
import math
import random
import sys
from collections import deque # Estructura de datos rápida para colas

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CARPETA_SONIDOS = os.path.join(DIRECTORIO_SCRIPT, "Sonidos")

ANCHO = 800
ALTO = 600
FONDO_BASE = (10, 10, 18) 

COLORES = {
    'Guitarra': (255, 220, 50),
    'Piano':    (255, 60, 140),
    'Bateria':  (60, 255, 180),
    'Trompeta': (60, 150, 255),
    'Bajo':     (180, 50, 255)
}

# CONFIGURACIÓN DEL BUFFER
TAMANO_PREBUFFER = 25 # Cuántas notas esperar antes de empezar a tocar
TIEMPO_ENTRE_NOTAS_MINIMO = 0.05 # Límite para que no suenen todas de golpe si se acumulan

ejecutando = False
banco_sonidos = {}
efectos_activos = []

# ==========================================
# 2. SISTEMA VISUAL (NEON DUST V2)
# ==========================================
class Particula:
    def __init__(self, x, y, color, scale=1.0):
        self.x = x + random.uniform(-10, 10)
        self.y = y + random.uniform(-10, 10)
        self.color = color
        angle = random.uniform(0, math.pi*2)
        speed = random.uniform(2, 8) * scale
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.vida = 255 
        self.tamano = random.randint(2, 4)

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 15

    def dibujar(self, surf):
        if self.vida > 0:
            s = pygame.Surface((self.tamano*2, self.tamano*2), pygame.SRCALPHA)
            c_alpha = (*self.color, self.vida)
            pygame.draw.circle(s, c_alpha, (self.tamano, self.tamano), self.tamano)
            surf.blit(s, (self.x - self.tamano, self.y - self.tamano))

class NeonDustShape:
    def __init__(self, instrumento, color):
        self.inst = instrumento
        self.color = color
        self.x = random.randint(100, ANCHO - 100)
        self.y = random.randint(100, ALTO - 100)
        self.radio_base = random.randint(30, 150)
        
        self.vida_forma = 1.0
        self.energia = 1.0
        self.tiempo_inicio = time.time()
        self.rotacion = random.uniform(0, math.pi*2)

        if self.inst == 'Bateria':
            self.num_ondas = random.randint(3, 4); self.vel_vib = 5.0; self.profundidad = 35; self.grosor = 5
        elif self.inst == 'Bajo': 
            self.num_ondas = 2; self.vel_vib = 2.0; self.profundidad = 40; self.grosor = 6
        elif self.inst == 'Guitarra':
            self.num_ondas = random.randint(10, 14); self.vel_vib = 18.0; self.profundidad = 15; self.grosor = 3
        else:
             self.num_ondas = 6; self.vel_vib = 10.0; self.profundidad = 12; self.grosor=3

        scale_factor = 1.0
        num_parts = 20
        if self.radio_base > 100:
            self.grosor += 3; num_parts = 40; scale_factor = 1.5
        
        self.particulas = []
        for _ in range(num_parts):
            self.particulas.append(Particula(self.x, self.y, self.color, scale_factor))

    def actualizar(self):
        self.vida_forma -= 0.03
        self.energia *= 0.90
        self.rotacion += 0.03
        for p in self.particulas: p.actualizar()
        self.particulas = [p for p in self.particulas if p.vida > 0]

    def dibujar(self, superficie):
        for p in self.particulas: p.dibujar(superficie)
        if self.vida_forma > 0:
            alpha = int(self.vida_forma * 255)
            s_temp = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            puntos = []
            resolucion = 100
            ahora = time.time() - self.tiempo_inicio
            for i in range(resolucion + 1):
                angulo = (i / resolucion) * 2 * math.pi
                vibracion = math.sin(angulo * self.num_ondas + ahora * self.vel_vib)
                r_final = self.radio_base + (vibracion * self.profundidad * self.energia)
                px = self.x + math.cos(angulo + self.rotacion) * r_final
                py = self.y + math.sin(angulo + self.rotacion) * r_final
                puntos.append((px, py))
            if len(puntos) > 2:
                pygame.draw.lines(s_temp, (*self.color, int(alpha/4)), True, puntos, self.grosor + 6)
                pygame.draw.lines(s_temp, (*self.color, alpha), True, puntos, self.grosor)
            superficie.blit(s_temp, (0,0))

    def esta_vivo(self):
        return self.vida_forma > 0 or len(self.particulas) > 0

# ==========================================
# 3. CARGA DE SONIDOS
# ==========================================
def cargar_instrumentos():
    global banco_sonidos
    print("Cargando sonidos...")
    for inst in COLORES.keys():
        banco_sonidos[inst] = {}
        ruta_inst = os.path.join(CARPETA_SONIDOS, inst)
        if not os.path.exists(ruta_inst): continue
        for archivo in os.listdir(ruta_inst):
            if archivo.endswith(".wav"):
                nota = os.path.splitext(archivo)[0]
                try:
                    s = pygame.mixer.Sound(os.path.join(ruta_inst, archivo))
                    s.set_volume(0.6)
                    if inst == 'Bateria': s.set_volume(0.9)
                    if inst == 'Bajo': s.set_volume(0.85)
                    banco_sonidos[inst][nota] = s
                except: pass

# ==========================================
# 4. PROCESAR COMANDO (Ej: "G-C4;")
# ==========================================
def reproducir_nota(trama):
    """ Toca la nota y crea el efecto visual """
    partes = trama.replace(';', '').split('-')
    if len(partes) < 2: return
    
    inst_letra, nota = partes[0], partes[1]
    
    mapa = {'G': 'Guitarra', 'B': 'Bateria', 'P': 'Piano', 'T': 'Trompeta', 'L': 'Bajo'}
    nombre_inst = mapa.get(inst_letra)
    
    if nombre_inst in banco_sonidos:
        if nota in banco_sonidos[nombre_inst]:
            banco_sonidos[nombre_inst][nota].play()
            efectos_activos.append(NeonDustShape(nombre_inst, COLORES[nombre_inst]))
        else:
            # Plan B: Random si falta la nota
            try:
                k = list(banco_sonidos[nombre_inst].keys())
                if k:
                    rand_n = random.choice(k)
                    banco_sonidos[nombre_inst][rand_n].play()
                    efectos_activos.append(NeonDustShape(nombre_inst, COLORES[nombre_inst]))
            except: pass

# ==========================================
# 5. FUNCIÓN PRINCIPAL (CON BUFFERING)
# ==========================================
def iniciar_visualizador_serial(puerto_serial_obj):
    global ejecutando, efectos_activos
    
    try:
        pygame.init()
        pygame.mixer.set_num_channels(64)
        pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("🎸 LI-FI CONCIERTO - BUFFERING... 🎸")
        reloj = pygame.time.Clock()
        
        superficie_estela = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        superficie_estela.fill((10, 10, 18, 40)) 
        
        cargar_instrumentos()
        efectos_activos = []
        ejecutando = True
        
        pantalla.fill(FONDO_BASE)
        pygame.display.flip()
        
        buffer_lectura_serial = "" # Buffer crudo del puerto COM
        cola_notas = deque()       # Buffer de notas listas para tocar
        
        reproduciendo = False
        ultimo_tiempo_nota = 0
        
        print("--- Esperando música (Llenando Buffer)... ---")

        while ejecutando:
            # A. EVENTOS
            for event in pygame.event.get():
                if event.type == pygame.QUIT: ejecutando = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: ejecutando = False
            
            # B. LEER SERIAL (LLENAR LA COLA)
            if puerto_serial_obj and puerto_serial_obj.in_waiting > 0:
                try:
                    datos = puerto_serial_obj.read(puerto_serial_obj.in_waiting).decode('ascii', errors='ignore')
                    buffer_lectura_serial += datos
                    
                    while ';' in buffer_lectura_serial:
                        comando, resto = buffer_lectura_serial.split(';', 1)
                        if '-' in comando:
                            cola_notas.append(comando) # Guardar en cola, NO tocar todavía
                        buffer_lectura_serial = resto
                except: pass

            # C. GESTIÓN DEL BUFFER (LOGICA DE REPRODUCCIÓN)
            
            # 1. Si no estamos reproduciendo, esperar a tener suficientes notas
            if not reproduciendo:
                # Mostrar mensaje de carga
                font = pygame.font.SysFont("Arial", 20)
                txt = font.render(f"Buffering: {len(cola_notas)}/{TAMANO_PREBUFFER}", True, (255, 255, 255))
                pantalla.blit(txt, (10, 10))
                
                if len(cola_notas) >= TAMANO_PREBUFFER:
                    reproduciendo = True
                    print("🚀 BUFFER LLENO -> ¡INICIANDO SHOW!")
            
            # 2. Si ya estamos reproduciendo, sacar notas de la cola
            else:
                ahora = time.time()
                # Sacamos nota si hay disponibles Y si pasó un tiempo mínimo (para evitar saturación)
                if len(cola_notas) > 0:
                    # Lógica simple: Intentar vaciar la cola a un ritmo constante
                    # Si el buffer se llena mucho, tocamos más rápido. Si se vacía, esperamos.
                    
                    if ahora - ultimo_tiempo_nota > TIEMPO_ENTRE_NOTAS_MINIMO:
                        nota_a_tocar = cola_notas.popleft()
                        reproducir_nota(nota_a_tocar)
                        ultimo_tiempo_nota = ahora
                else:
                    # Si se vacía el buffer, volvemos a modo espera
                    # Opcional: Podríamos dejarlo en reproduciendo si la conexión es rápida
                    # Pero para LiFi lento, mejor pausar si se acaba.
                    pass 

            # D. DIBUJAR VISUALES
            pantalla.blit(superficie_estela, (0,0))
            for efecto in efectos_activos[:]:
                efecto.actualizar()
                efecto.dibujar(pantalla)
                if not efecto.esta_vivo(): efectos_activos.remove(efecto)
            
            pygame.display.flip()
            reloj.tick(60)
            
        pygame.quit()
        
    except Exception as e:
        print(f"Error Pygame: {e}")
        pygame.quit()
