interfaz import tkinter as tk
from tkinter import messagebox, scrolledtext, Canvas
import serial
import time
import numpy as np
from PIL import Image, ImageFilter, ImageTk

# IMPORTAMOS TU MÓDULO DE EFECTOS VISUALES
import modulo_visualizador 

# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================
PUERTO = 'COM6'       
BAUDIOS = 2400        
# Configuración Imagen
ANCHO_IMG = 64
ALTO_IMG = 64
ESCALA_IMG = 5        

class LiFiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Receptor Li-Fi Integrado (Bit-Slicing)")
        self.root.geometry("900x700") 
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
        self.ser = None
        self.modo_actual = None 
        
        # Variables para recepción
        self.buffer_voto = []
        self.ultimo_tiempo = 0
        self.TIMEOUT = 0.1
        
        # Variables exclusivas de Imagen
        self.matriz_memoria = None
        self.x_actual = 0
        self.y_actual = 0
        self.img_tk_ref = None 
        
        self.crear_menu_principal()

    # ==========================================
    # NUEVA LÓGICA CENTRAL (BIT A BIT)
    # ==========================================
    def reconstruir_dato_bits(self, buffer, modo='texto'):
        if not buffer: return None

        n_muestras = len(buffer)
        umbral = n_muestras / 2.0
        
        valor_final = 0
        numeros = [ord(b) for b in buffer]
        
        rango_bits = 7 if modo == 'texto' else 8
        
        for i in range(rango_bits):
            mascara = 1 << i
            votos_uno = 0
            
            for num in numeros:
                if (num & mascara) != 0:
                    votos_uno += 1
            
            if votos_uno > umbral:
                valor_final |= mascara
        
        if modo == 'texto':
            valor_final = valor_final & 0x7F
            
        return valor_final

    # ==========================================
    # GESTIÓN SERIAL
    # ==========================================
    def cerrar_serial(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("🔒 Puerto Serial cerrado.")

    def abrir_serial(self):
        try:
            self.cerrar_serial() 
            self.ser = serial.Serial(PUERTO, BAUDIOS, timeout=0.01)
            print(f"✅ Conectado a {PUERTO}")
            return True
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo abrir {PUERTO}.\n\nError: {e}")
            return False

    # ==========================================
    # INTERFAZ: MENÚ PRINCIPAL
    # ==========================================
    def crear_menu_principal(self):
        self.limpiar_ventana()
        tk.Label(self.root, text="Receptor Li-Fi Multipropósito", font=("Arial", 20, "bold"), pady=20).pack()
        tk.Label(self.root, text="Seleccione el modo de operación:", font=("Arial", 12)).pack(pady=10)
        
        # BOTÓN TEXTO
        btn_texto = tk.Button(self.root, text="RECIBIR MENSAJES", 
                              font=("Arial", 14, "bold"), bg="#2196F3", fg="white", height=2, width=30,
                              command=self.iniciar_modo_texto)
        btn_texto.pack(pady=10)

        # BOTÓN IMAGEN
        btn_imagen = tk.Button(self.root, text="RECIBIR IMAGEN", 
                               font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", height=2, width=30,
                               command=self.iniciar_modo_imagen)
        btn_imagen.pack(pady=10)

        # --- AQUÍ ESTÁ EL NUEVO BOTÓN "MODO MÚSICA" ---
        btn_musica = tk.Button(self.root, text="MODO MÚSICA", 
                               font=("Arial", 14, "bold"), bg="#9C27B0", fg="white", height=2, width=30,
                               command=self.iniciar_modo_musica)
        btn_musica.pack(pady=10)
        
        tk.Label(self.root, text=f"Configurado en: {PUERTO} @ {BAUDIOS} baudios", fg="gray").pack(side=tk.BOTTOM, pady=10)

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def volver_al_menu(self):
        self.modo_actual = None
        self.cerrar_serial()
        self.crear_menu_principal()

    # ==========================================
    # MODO MÚSICA (CONECTADO AL MÓDULO PYGAME)
    # ==========================================
    def iniciar_modo_musica(self):
        """Lanza la ventana de Pygame y oculta Tkinter"""
        if not self.abrir_serial(): return
        
        # 1. Ocultar esta ventana principal
        self.root.withdraw()
        
        try:
            print("🚀 Iniciando Visualizador Neon Dust...")
            # 2. Llamamos a la función del otro archivo pasándole el puerto serial
            modulo_visualizador.iniciar_visualizador_serial(self.ser)
        except Exception as e:
            messagebox.showerror("Error Visualizador", f"Hubo un error en el módulo de música:\n{e}")
        
        # 3. Cuando cierres la ventana negra (Pygame), el código vuelve aquí:
        self.root.deiconify() # Mostrar ventana principal otra vez
        self.cerrar_serial()  # Cerrar puerto por seguridad
        print("🔙 Regresando al menú principal.")

    # ==========================================
    # MODO 1: RECEPCIÓN DE TEXTO
    # ==========================================
    def iniciar_modo_texto(self):
        if not self.abrir_serial(): return
        self.limpiar_ventana()
        self.modo_actual = 'texto'
        self.buffer_voto = []
        
        header_frame = tk.Frame(self.root)
        header_frame.pack(fill=tk.X, pady=5)
        tk.Label(header_frame, text="Modo: Recepción de Texto ", font=("Arial", 16, "bold"), bg="#E3F2FD").pack(side=tk.TOP, fill=tk.X)
        
        self.txt_display = scrolledtext.ScrolledText(self.root, font=("Consolas", 18), height=15, bg="black", fg="#00FF00")
        self.txt_display.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🧹 Limpiar Pantalla", command=self.limpiar_pantalla_texto, bg="#FFC107", fg="black", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="⬅ Volver al Menú", command=self.volver_al_menu, bg="#FF5722", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
        
        self.loop_texto()

    def limpiar_pantalla_texto(self):
        self.txt_display.delete('1.0', tk.END)

    def loop_texto(self):
        if self.modo_actual != 'texto': return
        try:
            if self.ser.in_waiting > 0:
                byte = self.ser.read()
                self.buffer_voto.append(byte)
                self.ultimo_tiempo = time.time()
                if len(self.buffer_voto) >= 5:
                    self.procesar_voto_texto()
            else:
                if len(self.buffer_voto) > 0 and (time.time() - self.ultimo_tiempo > self.TIMEOUT):
                    self.procesar_voto_texto()
        except: pass
        self.root.after(1, self.loop_texto)

    def procesar_voto_texto(self):
        if not self.buffer_voto: return
        val_reconstruido = self.reconstruir_dato_bits(self.buffer_voto, modo='texto')
        self.buffer_voto = [] 
        if val_reconstruido is not None:
            if 32 <= val_reconstruido <= 126 or val_reconstruido == 10 or val_reconstruido == 13:
                caracter = chr(val_reconstruido)
                self.txt_display.insert(tk.END, caracter)
                self.txt_display.see(tk.END)

    # ==========================================
    # MODO 2: RECEPCIÓN DE IMAGEN
    # ==========================================
    def iniciar_modo_imagen(self):
        if not self.abrir_serial(): return
        self.limpiar_ventana()
        self.modo_actual = 'imagen'
        self.matriz_memoria = np.zeros((ALTO_IMG, ANCHO_IMG), dtype=np.uint8)
        self.x_actual = 0; self.y_actual = 0
        self.buffer_voto = []
        
        tk.Label(self.root, text="Modo: Reconstrucción de Imagen", font=("Arial", 16, "bold"), bg="#E8F5E9").pack(pady=5, fill=tk.X)
        self.lbl_estado_img = tk.Label(self.root, text="Esperando datos...", fg="blue", font=("Arial", 12))
        self.lbl_estado_img.pack()
        
        frame_lienzos = tk.Frame(self.root)
        frame_lienzos.pack(pady=10)
        
        tk.Label(frame_lienzos, text="Recepción en Vivo", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=20)
        self.canvas_raw = Canvas(frame_lienzos, width=ANCHO_IMG*ESCALA_IMG, height=ALTO_IMG*ESCALA_IMG, bg="black")
        self.canvas_raw.grid(row=1, column=0, padx=20)
        
        tk.Label(frame_lienzos, text="Imagen Filtrada", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=20)
        self.canvas_filter = Canvas(frame_lienzos, width=ANCHO_IMG*ESCALA_IMG, height=ALTO_IMG*ESCALA_IMG, bg="#222")
        self.canvas_filter.grid(row=1, column=1, padx=20)
        
        frame_botones = tk.Frame(self.root)
        frame_botones.pack(pady=15)
        tk.Button(frame_botones, text="✨ Aplicar Filtro", command=self.aplicar_filtro_manual, bg="#9C27B0", fg="white", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botones, text="🗑 Reiniciar", command=self.reset_imagen, bg="#FFC107", fg="black", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botones, text="⬅ Volver", command=self.volver_al_menu, bg="#FF5722", fg="white", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=10)
        
        self.loop_imagen()

    def loop_imagen(self):
        if self.modo_actual != 'imagen': return
        try:
            if self.ser.in_waiting > 0:
                byte = self.ser.read()
                self.buffer_voto.append(byte)
                self.ultimo_tiempo = time.time()
                if len(self.buffer_voto) >= 3:
                    self.procesar_pixel()
            else:
                if len(self.buffer_voto) > 0 and (time.time() - self.ultimo_tiempo > self.TIMEOUT):
                    self.procesar_pixel()
        except: pass
        self.root.after(1, self.loop_imagen)

    def procesar_pixel(self):
        if not self.buffer_voto: return
        val = self.reconstruir_dato_bits(self.buffer_voto, modo='imagen')
        self.buffer_voto = []
        if val is None: return

        if self.y_actual < ALTO_IMG and self.x_actual < ANCHO_IMG:
            self.matriz_memoria[self.y_actual, self.x_actual] = val
            hex_color = f'#{val:02x}{val:02x}{val:02x}'
            x1 = self.x_actual * ESCALA_IMG
            y1 = self.y_actual * ESCALA_IMG
            self.canvas_raw.create_rectangle(x1, y1, x1+ESCALA_IMG, y1+ESCALA_IMG, fill=hex_color, outline="")
            self.x_actual += 1
            if self.x_actual >= ANCHO_IMG:
                self.x_actual = 0
                self.y_actual += 1
                porcentaje = int((self.y_actual / ALTO_IMG) * 100)
                if porcentaje <= 100:
                    self.lbl_estado_img.config(text=f"Recibiendo: {porcentaje}% completado...", fg="blue")
                self.root.update_idletasks()
                if self.y_actual >= ALTO_IMG:
                    self.lbl_estado_img.config(text="✅ Recepción Finalizada.", fg="green")

    def aplicar_filtro_manual(self):
        self.lbl_estado_img.config(text="Procesando filtro...", fg="orange")
        self.root.update()
        img_cruda = Image.fromarray(self.matriz_memoria, 'L')
        img_limpia = img_cruda.filter(ImageFilter.MedianFilter(size=3))
        img_grande = img_limpia.resize((ANCHO_IMG*ESCALA_IMG, ALTO_IMG*ESCALA_IMG), Image.NEAREST)
        self.img_tk_ref = ImageTk.PhotoImage(img_grande)
        self.canvas_filter.delete("all")
        self.canvas_filter.create_image(0, 0, anchor=tk.NW, image=self.img_tk_ref)
        self.lbl_estado_img.config(text="Filtro Aplicado.", fg="purple")

    def reset_imagen(self):
        self.x_actual = 0; self.y_actual = 0
        self.matriz_memoria = np.zeros((ALTO_IMG, ANCHO_IMG), dtype=np.uint8)
        self.buffer_voto = []
        self.canvas_raw.delete("all")
        self.canvas_filter.delete("all")
        self.lbl_estado_img.config(text="Lienzo blanqueado.", fg="blue")

    def cerrar_aplicacion(self):
        self.cerrar_serial()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LiFiApp(root)
    root.mainloop()
