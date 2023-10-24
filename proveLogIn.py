import tkinter as tk
from tkinter import messagebox

# Función para verificar las credenciales ingresadas por el usuario
def verificar_credenciales():
    usuario = usuario_entry.get()
    contrasena = contrasena_entry.get()

    # Verificar las credenciales (aquí puedes realizar la verificación con tus propias credenciales)
    if usuario == "usuario" and contrasena == "contrasena":
        root.destroy()  # Cerrar la ventana de inicio de sesión
        mostrar_ventana_bienvenida()
    else:
        messagebox.showerror("Error", "Credenciales incorrectas")

# Función para mostrar la ventana de bienvenida
def mostrar_ventana_bienvenida():
    ventana_bienvenida = tk.Tk()
    ventana_bienvenida.title("Bienvenido")
    ventana_bienvenida.geometry("560x560")

    etiqueta_bienvenida = tk.Label(ventana_bienvenida, text="¡Bienvenido!")
    etiqueta_bienvenida.pack()

# Crear una ventana principal de tamaño 560x560
root = tk.Tk()
root.title("Inicio de Sesión")
root.geometry("560x560")

# Etiquetas y campos de entrada para usuario y contraseña
usuario_label = tk.Label(root, text="Usuario:")
usuario_label.pack()
usuario_entry = tk.Entry(root)
usuario_entry.pack()

contrasena_label = tk.Label(root, text="Contraseña:")
contrasena_label.pack()
contrasena_entry = tk.Entry(root, show="*")  # Para ocultar la contraseña
contrasena_entry.pack()

# Botón para iniciar sesión
boton_ingresar = tk.Button(root, text="Ingresar", command=verificar_credenciales)
boton_ingresar.pack()

# Ejecutar el bucle principal de la aplicación
root.mainloop()
