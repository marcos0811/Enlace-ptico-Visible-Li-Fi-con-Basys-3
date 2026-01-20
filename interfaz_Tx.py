import serial
import time
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import threading
import os
import mido  

# ==========================================
#  CONFIGURACIÓN GLOBAL
# ==========================================
PUERTO = 'COM6'  
BAUDIOS = 2400

PLAYLIST = {
    1: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\gorillaz-clint_eastwood.mid",
    2: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\Seven_Nation_Army.mid",
    3: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\LA BOUCHE.Sweet dreams K.mid",
    4: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\Marilyn Manson - Sweet Dreams.mid",
    5: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\Michael Jackson - Billie Jean.mid",
    6: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\MGMT_-_Kids.mid",
    7: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\Mgmt - Electric Feel.mid",
    8: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\Another-One-Bites-The-Dust-1.mid",
    9: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\Another-One-Bites-The-Dust-2.mid",
    10: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\Arctic Monkeys - Do I Wanna Know_.mid",
    11: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\gorillaz-feel_good_inc.mid",
    12: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\Daft Punk - Get Lucky.mid",
    13: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\Eye-Of-The-Tiger-(From-'Rocky').mid",
    14: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musicas_mid\DaftPunkftPharellGetLucky.mid",
    15: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musica\Zoe — Labios Rotos [MIDIfind.com].mid",
    16: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musica\Shrek.mid",
    17: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musica\La_pantera_rosa.mid",
    18: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musica\El_rey_leon_(Hakuna_matata).mid",
    19: r"C:\Users\japam\OneDrive\Documentos\Ciclos\6.Sexto Ciclo\Programacion en VHDL\musica\La_bella_y_la_bestia.mid",
}

# Mapeo de notas musicales
NOTAS = ['C', 'Cs', 'D', 'Ds', 'E', 'F', 'Fs', 'G', 'Gs', 'A', 'As', 'B']

# Banderas de control
cancelar_transmision = False
cancelar_musica = False

# ==========================================
#  FUNCIONES AUXILIARES
# ==========================================


def nota_midi_a_texto(note_num):
    """Convierte nota MIDI (0-127) a texto (ej: C4)"""
    octava = (note_num // 12) - 1
    idx = note_num % 12
    nombre = NOTAS[idx]

    if octava < 3:
        octava = 3
    if octava > 5:
        octava = 5

    return f"{nombre}{octava}"


def abrir_serial():
    """Abre la conexión serial"""
    ser = serial.Serial(
        PUERTO, BAUDIOS, stopbits=serial.STOPBITS_TWO, timeout=1)
    time.sleep(2)
    return ser


def detener_envio_principal():
    """Detiene envío de Texto/Imagen en la ventana principal"""
    global cancelar_transmision
    cancelar_transmision = True
    consola.insert(tk.END, "\n\n⛔ DETENIENDO TRANSMISIÓN... ESPERE...\n")
    consola.see(tk.END)

# ==========================================
#  VENTANA DE MUSICA
# ==========================================


def abrir_ventana_musica():
    ventana_musica = tk.Toplevel(ventana)
    ventana_musica.title("🎵 DJ Láser - Playlist VHDL")
    ventana_musica.geometry("600x600")
    ventana_musica.resizable(False, False)

    lbl_lista = tk.Label(
        ventana_musica, text="Selecciona una canción:", font=("Arial", 11, "bold"))
    lbl_lista.pack(pady=(15, 5))

    frame_lista = tk.Frame(ventana_musica)
    frame_lista.pack(pady=5, padx=20, fill="x")

    scrollbar = tk.Scrollbar(frame_lista)
    scrollbar.pack(side="right", fill="y")

    lista_box = tk.Listbox(frame_lista, height=10, font=(
        "Arial", 10), selectmode=tk.SINGLE, yscrollcommand=scrollbar.set)
    lista_box.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=lista_box.yview)

    # Llenar la lista con tu Playlist
    rutas_ordenadas = []
    for key in sorted(PLAYLIST.keys()):  
        ruta = PLAYLIST[key]
        nombre_archivo = os.path.basename(ruta)
        lista_box.insert(tk.END, f"{key}. {nombre_archivo}")
        rutas_ordenadas.append(ruta)

    # --- Consola de musica ---
    txt_consola_musica = tk.Text(
        ventana_musica, height=12, width=60, bg="black", fg="#00FF00", font=("Consolas", 9))
    txt_consola_musica.pack(pady=10, padx=10)

    # --- Lógica de Reproducción ---
    def ejecutar_musica():
        global cancelar_musica

        indice_seleccionado = lista_box.curselection()
        if not indice_seleccionado:
            messagebox.showwarning(
                "Atención", "Por favor selecciona una canción de la lista.")
            return

        idx = indice_seleccionado[0]
        archivo = rutas_ordenadas[idx]  # Obtener ruta real

        if not os.path.exists(archivo):
            messagebox.showerror(
                "Error", f"No se encuentra el archivo:\n{archivo}")
            return

        try:
            txt_consola_musica.delete(1.0, tk.END)
            txt_consola_musica.insert(tk.END, f"🔌 Conectando a {PUERTO}...\n")
            ser = serial.Serial(
                PUERTO, BAUDIOS, stopbits=serial.STOPBITS_TWO, timeout=1)
            time.sleep(2)

            mid = mido.MidiFile(archivo)
            txt_consola_musica.insert(
                tk.END, f"▶ REPRODUCIENDO: {os.path.basename(archivo)}\n")
            txt_consola_musica.insert(
                tk.END, f"----------------------------------\n")

            for msg in mid.play():
                if cancelar_musica:
                    txt_consola_musica.insert(
                        tk.END, "\n🛑 Música detenida por usuario.\n")
                    break

                if msg.type == 'note_on' and msg.velocity > 0:
                    # Determinar instrumento
                    inst = 'G'
                    if msg.channel == 9:
                        inst = 'B'
                    elif msg.note < 53:
                        inst = 'L'
                    elif msg.note > 75:
                        inst = 'T'

                    # Convertir y enviar
                    nota_txt = nota_midi_a_texto(msg.note)
                    trama = f"{inst}-{nota_txt};"

                    ser.write(trama.encode('ascii'))
                    txt_consola_musica.insert(tk.END, f"-> {trama}\n")
                    txt_consola_musica.see(tk.END)

            ser.close()
            txt_consola_musica.insert(tk.END, "🏁 Fin de canción.\n")

            # Restaurar interfaz
            btn_play.config(state="normal")
            btn_stop.config(state="disabled")
            lista_box.config(state="normal")

        except Exception as e:
            messagebox.showerror("Error MIDI", str(e))
            btn_play.config(state="normal")
            lista_box.config(state="normal")

    def iniciar_hilo_musica():
        global cancelar_musica
        cancelar_musica = False
        btn_play.config(state="disabled")
        btn_stop.config(state="normal")
        # Bloquear cambios durante reproducción
        lista_box.config(state="disabled")

        t = threading.Thread(target=ejecutar_musica)
        t.daemon = True
        t.start()

    def detener_musica_btn():
        global cancelar_musica
        cancelar_musica = True
        btn_stop.config(state="disabled")

    # Botones de control
    frame_controles = tk.Frame(ventana_musica)
    frame_controles.pack(pady=10)

    btn_play = tk.Button(frame_controles, text="▶ REPRODUCIR", bg="green", fg="white",
                         command=iniciar_hilo_musica, width=15, font=("Arial", 11, "bold"))
    btn_play.pack(side="left", padx=10)

    btn_stop = tk.Button(frame_controles, text="⏹ DETENER", bg="red", fg="white",
                         command=detener_musica_btn, state="disabled", width=15, font=("Arial", 11, "bold"))
    btn_stop.pack(side="left", padx=10)


# ==========================================
#  FUNCIONES PRINCIPALES (Texto / Imagen)
# ==========================================
def enviar_texto():
    global cancelar_transmision
    mensaje = entrada_texto.get()

    if mensaje == "":
        return

    cancelar_transmision = False
    boton_texto.config(state="disabled")
    btn_env_img.config(state="disabled")
    btn_musica.config(state="disabled")
    led_estado.config(bg="red")

    consola.insert(tk.END, "\n--- Enviando TEXTO ---\n")

    try:
        ser = abrir_serial()
        for caracter in mensaje:
            if cancelar_transmision:
                consola.insert(tk.END, "\n[X] Envío cancelado.\n")
                break

            byte_dato = caracter.encode('ascii', errors='replace')
            # Enviamos 5 veces por redundancia
            for _ in range(5):
                ser.write(byte_dato)
                ser.flush()
                time.sleep(0.02)

            estado_caracter.config(text=f"Enviando: '{caracter}'")
            led_estado.config(bg="green")
            consola.insert(tk.END, caracter)
            consola.see(tk.END)
            ventana.update()
            time.sleep(0.15)

        ser.close()
        if not cancelar_transmision:
            consola.insert(tk.END, "\n✔ Texto enviado correctamente\n")

    except Exception as e:
        messagebox.showerror("Error Serial", str(e))
        consola.insert(tk.END, f"\nError: {e}\n")

    # Restaurar
    led_estado.config(bg="red")
    boton_texto.config(state="normal")
    btn_env_img.config(state="normal")
    btn_musica.config(state="normal")
    estado_caracter.config(text="...")


def seleccionar_imagen():
    global img_procesada, img_preview
    ruta = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=[
                                      ("Images", "*.jpg *.png *.bmp")])
    if not ruta:
        return

    img_original = Image.open(ruta)
    # Convertir a 64x64 Blanco y Negro
    img_procesada = img_original.resize((64, 64)).convert('L')

    # Preview más grande para la interfaz
    img_preview = ImageTk.PhotoImage(img_procesada.resize((128, 128)))
    label_img.config(image=img_preview)
    consola.insert(tk.END, "Imagen cargada y lista para enviar\n")


def enviar_imagen():
    global img_reconstruida, img_recon_tk, cancelar_transmision

    if img_procesada is None:
        messagebox.showwarning("Aviso", "Primero selecciona una imagen")
        return

    cancelar_transmision = False
    boton_texto.config(state="disabled")
    btn_env_img.config(state="disabled")
    btn_musica.config(state="disabled")

    consola.insert(tk.END, "\n--- Enviando IMAGEN ---\n")
    img_reconstruida = Image.new('L', (64, 64), 0)

    try:
        ser = abrir_serial()
        datos_pixel = list(img_procesada.getdata())
        fila_buffer = []
        fila_actual = 0

        for i, pixel in enumerate(datos_pixel):
            if cancelar_transmision:
                consola.insert(tk.END, "\nEnvío de IMAGEN cancelado.\n")
                break

            byte_dato = bytes([pixel])
            # Redundancia x3
            for _ in range(3):
                ser.write(byte_dato)
                ser.flush()
                time.sleep(0.005)

            fila_buffer.append(pixel)
            time.sleep(0.08)  # Pausa entre pixeles

            # Reconstruir en pantalla cada 64 pixeles
            if len(fila_buffer) == 64:
                for col in range(64):
                    img_reconstruida.putpixel(
                        (col, fila_actual), fila_buffer[col])

                fila_actual += 1
                fila_buffer.clear()

                img_recon_tk = ImageTk.PhotoImage(
                    img_reconstruida.resize((128, 128)))
                label_recon.config(image=img_recon_tk)
                label_recon.image = img_recon_tk
                consola.insert(tk.END, f"Fila {fila_actual} enviada\n")
                consola.see(tk.END)
                ventana.update()

        ser.close()
        if not cancelar_transmision:
            consola.insert(tk.END, "Imagen enviada correctamente\n")

    except Exception as e:
        consola.insert(tk.END, f"Error: {e}\n")

    boton_texto.config(state="normal")
    btn_env_img.config(state="normal")
    btn_musica.config(state="normal")


# ==========================================
#  INTERFAZ GRÁFICA PRINCIPAL
# ==========================================
ventana = tk.Tk()
ventana.title("Transmisor VHDL Li-Fi")
ventana.geometry("700x750")
ventana.resizable(False, False)

# 1. Botón Pánico (Principal)
frame_panico = tk.Frame(ventana, pady=5)
frame_panico.pack(fill="x")
btn_cancelar = tk.Button(frame_panico, text="DETENER ENVÍO (Texto/Img)", command=detener_envio_principal,
                         bg="#D32F2F", fg="white", font=("Arial", 12, "bold"), height=2)
btn_cancelar.pack(fill="x", padx=20)

# 2. Sección Música (NUEVA)
frame_musica = tk.LabelFrame(
    ventana, text="🎵 Modo Musical (MIDI)", padx=10, pady=10, bg="#E8F5E9")
frame_musica.pack(fill="x", padx=10, pady=5)

lbl_musica = tk.Label(
    frame_musica, text="Transmisión de Notas Musicales por Láser", bg="#E8F5E9", font=("Arial", 10))
lbl_musica.pack(side="left", padx=10)

btn_musica = tk.Button(frame_musica, text="ABRIR PLAYLIST", command=abrir_ventana_musica,
                       bg="#673AB7", fg="white", font=("Arial", 10, "bold"), width=20)
btn_musica.pack(side="right", padx=10)

# 3. Sección Texto
frame_texto = tk.LabelFrame(ventana, text="📄 Envío de Texto", padx=10, pady=10)
frame_texto.pack(fill="x", padx=10, pady=5)

entrada_texto = tk.Entry(frame_texto, width=40, font=("Consolas", 12))
entrada_texto.grid(row=0, column=0, padx=5)

boton_texto = tk.Button(frame_texto, text="ENVIAR TEXTO",
                        command=enviar_texto, bg="#2196F3", fg="white")
boton_texto.grid(row=0, column=1, padx=5)

estado_caracter = tk.Label(frame_texto, text="Letras enviadas:")
estado_caracter.grid(row=1, column=0, pady=5)

led_estado = tk.Label(frame_texto, bg="red", width=4, height=1)
led_estado.grid(row=1, column=1)

# 4. Sección Imagen
frame_img = tk.LabelFrame(ventana, text="📷 Envío de Imagen", padx=10, pady=10)
frame_img.pack(fill="x", padx=10, pady=5)

btn_img = tk.Button(frame_img, text="Seleccionar Imagen",
                    command=seleccionar_imagen)
btn_img.grid(row=0, column=0, padx=5)

btn_env_img = tk.Button(frame_img, text="ENVIAR IMAGEN",
                        command=enviar_imagen, bg="#4CAF50", fg="white")
btn_env_img.grid(row=0, column=1, padx=5)

label_img = tk.Label(frame_img)
label_img.grid(row=1, column=0, padx=(10, 30), pady=10)
label_recon = tk.Label(frame_img)
label_recon.grid(row=1, column=1, padx=(40, 10), pady=10)

img_procesada = None
img_preview = None

# 5. Consola Principal
frame_consola = tk.LabelFrame(
    ventana, text="🖥 Consola Serial", padx=10, pady=10)
frame_consola.pack(fill="both", expand=True, padx=10, pady=5)

consola = tk.Text(frame_consola, height=10, font=("Consolas", 10))
consola.pack(fill="both", expand=True)

ventana.mainloop()
