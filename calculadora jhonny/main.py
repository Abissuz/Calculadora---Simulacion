import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import math

# Funciones para calcular los modelos de colas
def calcular_sin_limite_cola(lambda_, mu):
    rho = lambda_ / mu
    Po = 1 - rho
    Ls = lambda_ / (mu - lambda_)
    Lq = Ls - rho
    Ws = Ls / lambda_
    Wq = Lq / lambda_
    lambda_efectiva = lambda_
    
    # Distribución de probabilidad
    n = 10  # Número de estados a considerar
    probabilidades_absolutas = [Po * (rho ** i) for i in range(n)]
    probabilidades_acumuladas = [sum(probabilidades_absolutas[:i+1]) for i in range(n)]
    
    return {
        "lambda": lambda_,
        "mu": mu,
        "rho": rho,
        "Po": Po,
        "Ls": Ls,
        "Lq": Lq,
        "Ws": Ws,
        "Wq": Wq,
        "lambda_efectiva": lambda_efectiva,
        "probabilidades_absolutas": probabilidades_absolutas,
        "probabilidades_acumuladas": probabilidades_acumuladas
    }

def calcular_con_limite_cola(lambda_, mu, N):
    rho = lambda_ / mu
    Po = (1 - rho) / (1 - rho ** (N + 1))
    Ls = (rho * (1 - (N + 1) * rho ** N + N * rho ** (N + 1))) / ((1 - rho) * (1 - rho ** (N + 1)))
    Lq = Ls - (1 - Po)
    lambda_efectiva = lambda_ * (1 - Po)
    Ws = Ls / lambda_efectiva
    Wq = Lq / lambda_efectiva
    
    # Distribución de probabilidad
    n = N + 1  # Número de estados a considerar
    probabilidades_absolutas = [Po * (rho ** i) for i in range(n)]
    probabilidades_acumuladas = [sum(probabilidades_absolutas[:i+1]) for i in range(n)]
    
    return {
        "lambda": lambda_,
        "mu": mu,
        "rho": rho,
        "Po": Po,
        "Ls": Ls,
        "Lq": Lq,
        "Ws": Ws,
        "Wq": Wq,
        "lambda_efectiva": lambda_efectiva,
        "probabilidades_absolutas": probabilidades_absolutas,
        "probabilidades_acumuladas": probabilidades_acumuladas
    }

# Función para generar el reporte en PDF
def generar_reporte(resultados, filename="reporte.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "Reporte de Modelo de Colas")
    
    y = 700
    for key, value in resultados.items():
        if key in ["probabilidades_absolutas", "probabilidades_acumuladas"]:
            c.drawString(100, y, f"{key}:")
            y -= 20
            for i, val in enumerate(value):
                c.drawString(120, y, f"Estado {i}: {val:.4f}")
                y -= 20
        else:
            c.drawString(100, y, f"{key}: {value:.4f}")
            y -= 20
    
    c.save()
    messagebox.showinfo("Reporte Generado", f"El reporte se ha guardado en {filename}")

# Interfaz gráfica mejorada con estilos
class CalculadoraColas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora de Modelos de Colas")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        # Estilos personalizados
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Tema moderno
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 12), foreground="#333")
        self.style.configure("TButton", font=("Arial", 12), padding=10, background="#4CAF50", foreground="white")
        self.style.map("TButton", background=[("active", "#45a049")])
        self.style.configure("TEntry", font=("Arial", 12), padding=5)
        
        # Frame principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Selección de modelo
        self.label_modelo = ttk.Label(self.main_frame, text="Selecciona el modelo de colas:")
        self.label_modelo.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.boton_sin_limite = ttk.Button(self.main_frame, text="Sin límite en cola", command=self.abrir_sin_limite)
        self.boton_sin_limite.grid(row=1, column=0, padx=10, pady=10)
        
        self.boton_con_limite = ttk.Button(self.main_frame, text="Con límite en cola", command=self.abrir_con_limite)
        self.boton_con_limite.grid(row=1, column=1, padx=10, pady=10)
    
    def abrir_sin_limite(self):
        self.withdraw()  # Oculta la ventana principal
        VentanaSinLimite(self)
    
    def abrir_con_limite(self):
        self.withdraw()  # Oculta la ventana principal
        VentanaConLimite(self)

class VentanaSinLimite(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Modelo sin límite en cola")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        # Frame principal con barra de desplazamiento
        self.canvas = tk.Canvas(self, bg="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Frame para los campos de entrada y resultados
        self.left_frame = ttk.Frame(self.scrollable_frame)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        
        # Frame para el historial
        self.right_frame = ttk.Frame(self.scrollable_frame)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        
        # Entradas
        self.label_lambda = ttk.Label(self.left_frame, text="Tasa de llegada (λ):")
        self.label_lambda.grid(row=0, column=0, padx=10, pady=10)
        self.entry_lambda = ttk.Entry(self.left_frame)
        self.entry_lambda.grid(row=0, column=1, padx=10, pady=10)
        
        self.label_mu = ttk.Label(self.left_frame, text="Tasa de servicio (μ):")
        self.label_mu.grid(row=1, column=0, padx=10, pady=10)
        self.entry_mu = ttk.Entry(self.left_frame)
        self.entry_mu.grid(row=1, column=1, padx=10, pady=10)
        
        # Botón de cálculo
        self.boton_calcular = ttk.Button(self.left_frame, text="Calcular", command=self.calcular)
        self.boton_calcular.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Frame de resultados
        self.resultados_frame = ttk.Frame(self.left_frame)
        self.resultados_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Botón de descarga
        self.boton_descargar = ttk.Button(self.left_frame, text="Descargar resultados", command=self.descargar_resultados)
        self.boton_descargar.grid(row=4, column=0, columnspan=2, pady=10)
        self.boton_descargar.grid_remove()  # Ocultar inicialmente
        
        # Botón de retroceso
        self.boton_retroceso = ttk.Button(self.left_frame, text="Volver", command=self.volver)
        self.boton_retroceso.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Historial
        self.label_historial = ttk.Label(self.right_frame, text="Historial", font=("Arial", 14, "bold"))
        self.label_historial.grid(row=0, column=0, pady=10)
        
        self.tree_historial = ttk.Treeview(self.right_frame, columns=("λ", "μ", "ρ"), show="headings")
        self.tree_historial.heading("λ", text="λ")
        self.tree_historial.heading("μ", text="μ")
        self.tree_historial.heading("ρ", text="ρ")
        self.tree_historial.grid(row=1, column=0, padx=10, pady=10)
        
        # Barra de desplazamiento para el historial
        scrollbar_historial = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree_historial.yview)
        scrollbar_historial.grid(row=1, column=1, sticky="ns")
        self.tree_historial.configure(yscrollcommand=scrollbar_historial.set)
    
    def calcular(self):
        try:
            lambda_ = float(self.entry_lambda.get())
            mu = float(self.entry_mu.get())
            self.resultados = calcular_sin_limite_cola(lambda_, mu)
            self.mostrar_resultados()
            self.boton_descargar.grid()  # Mostrar botón de descarga
            
            # Agregar al historial
            self.tree_historial.insert("", "end", values=(lambda_, mu, f"{self.resultados['rho']:.4f}"))
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa valores numéricos válidos.")
    
    def mostrar_resultados(self):
        # Limpiar frame de resultados
        for widget in self.resultados_frame.winfo_children():
            widget.destroy()
        
        # Mostrar resultados
        ttk.Label(self.resultados_frame, text="Resultados", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.resultados_frame, text=f"Tasa de llegada (λ): {self.resultados['lambda']}").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Tasa de servicio (μ): {self.resultados['mu']}").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Rho (ρ): {self.resultados['rho']:.4f}").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Probabilidad de sistema vacío (P₀): {self.resultados['Po']:.4f}").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Número esperado en el sistema (L): {self.resultados['Ls']:.4f}").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Número esperado en la cola (Lq): {self.resultados['Lq']:.4f}").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Tiempo esperado en el sistema (W): {self.resultados['Ws']:.4f}").grid(row=7, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Tiempo esperado en la cola (Wq): {self.resultados['Wq']:.4f}").grid(row=8, column=0, sticky="w", padx=10, pady=5)
        
        # Mostrar distribución de probabilidad
        ttk.Label(self.resultados_frame, text="Distribución de Probabilidad", font=("Arial", 14, "bold")).grid(row=9, column=0, columnspan=2, pady=10)
        
        # Crear Treeview para la tabla
        self.tree = ttk.Treeview(self.resultados_frame, columns=("Estado", "P(n)", "P(Acum)"), show="headings")
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("P(n)", text="P(n)")
        self.tree.heading("P(Acum)", text="P(Acum)")
        self.tree.grid(row=10, column=0, columnspan=2, padx=10, pady=10)
        
        # Agregar barra de desplazamiento
        scrollbar = ttk.Scrollbar(self.resultados_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=10, column=2, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Llenar la tabla con los datos
        for i, (p_abs, p_acum) in enumerate(zip(self.resultados["probabilidades_absolutas"], self.resultados["probabilidades_acumuladas"])):
            self.tree.insert("", "end", values=(i, f"{p_abs:.4f}", f"{p_acum:.4f}"))
    
    def descargar_resultados(self):
        generar_reporte(self.resultados)
        messagebox.showinfo("Descarga completada", "Los resultados se han descargado en formato PDF.")
    
    def volver(self):
        self.destroy()  # Cierra esta ventana
        self.master.deiconify()  # Muestra la ventana principal

class VentanaConLimite(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Modelo con límite en cola")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        # Frame principal con barra de desplazamiento
        self.canvas = tk.Canvas(self, bg="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Frame para los campos de entrada y resultados
        self.left_frame = ttk.Frame(self.scrollable_frame)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        
        # Frame para el historial
        self.right_frame = ttk.Frame(self.scrollable_frame)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        
        # Entradas
        self.label_lambda = ttk.Label(self.left_frame, text="Tasa de llegada (λ):")
        self.label_lambda.grid(row=0, column=0, padx=10, pady=10)
        self.entry_lambda = ttk.Entry(self.left_frame)
        self.entry_lambda.grid(row=0, column=1, padx=10, pady=10)
        
        self.label_mu = ttk.Label(self.left_frame, text="Tasa de servicio (μ):")
        self.label_mu.grid(row=1, column=0, padx=10, pady=10)
        self.entry_mu = ttk.Entry(self.left_frame)
        self.entry_mu.grid(row=1, column=1, padx=10, pady=10)
        
        self.label_N = ttk.Label(self.left_frame, text="Límite de cola (N):")
        self.label_N.grid(row=2, column=0, padx=10, pady=10)
        self.entry_N = ttk.Entry(self.left_frame)
        self.entry_N.grid(row=2, column=1, padx=10, pady=10)
        
        # Botón de cálculo
        self.boton_calcular = ttk.Button(self.left_frame, text="Calcular", command=self.calcular)
        self.boton_calcular.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Frame de resultados
        self.resultados_frame = ttk.Frame(self.left_frame)
        self.resultados_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Botón de descarga
        self.boton_descargar = ttk.Button(self.left_frame, text="Descargar resultados", command=self.descargar_resultados)
        self.boton_descargar.grid(row=5, column=0, columnspan=2, pady=10)
        self.boton_descargar.grid_remove()  # Ocultar inicialmente
        
        # Botón de retroceso
        self.boton_retroceso = ttk.Button(self.left_frame, text="Volver", command=self.volver)
        self.boton_retroceso.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Historial
        self.label_historial = ttk.Label(self.right_frame, text="Historial", font=("Arial", 14, "bold"))
        self.label_historial.grid(row=0, column=0, pady=10)
        
        self.tree_historial = ttk.Treeview(self.right_frame, columns=("λ", "μ", "N", "ρ"), show="headings")
        self.tree_historial.heading("λ", text="λ")
        self.tree_historial.heading("μ", text="μ")
        self.tree_historial.heading("N", text="N")
        self.tree_historial.heading("ρ", text="ρ")
        self.tree_historial.grid(row=1, column=0, padx=10, pady=10)
        
        # Barra de desplazamiento para el historial
        scrollbar_historial = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.tree_historial.yview)
        scrollbar_historial.grid(row=1, column=1, sticky="ns")
        self.tree_historial.configure(yscrollcommand=scrollbar_historial.set)
    
    def calcular(self):
        try:
            lambda_ = float(self.entry_lambda.get())
            mu = float(self.entry_mu.get())
            N = int(self.entry_N.get())
            self.resultados = calcular_con_limite_cola(lambda_, mu, N)
            self.mostrar_resultados()
            self.boton_descargar.grid()  # Mostrar botón de descarga
            
            # Agregar al historial
            self.tree_historial.insert("", "end", values=(lambda_, mu, N, f"{self.resultados['rho']:.4f}"))
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa valores numéricos válidos.")
    
    def mostrar_resultados(self):
        # Limpiar frame de resultados
        for widget in self.resultados_frame.winfo_children():
            widget.destroy()
        
        # Mostrar resultados
        ttk.Label(self.resultados_frame, text="Resultados", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.resultados_frame, text=f"Tasa de llegada (λ): {self.resultados['lambda']}").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Tasa de servicio (μ): {self.resultados['mu']}").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Rho (ρ): {self.resultados['rho']:.4f}").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Probabilidad de sistema vacío (P₀): {self.resultados['Po']:.4f}").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Número esperado en el sistema (L): {self.resultados['Ls']:.4f}").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Número esperado en la cola (Lq): {self.resultados['Lq']:.4f}").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Tiempo esperado en el sistema (W): {self.resultados['Ws']:.4f}").grid(row=7, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(self.resultados_frame, text=f"Tiempo esperado en la cola (Wq): {self.resultados['Wq']:.4f}").grid(row=8, column=0, sticky="w", padx=10, pady=5)
        
        # Mostrar distribución de probabilidad
        ttk.Label(self.resultados_frame, text="Distribución de Probabilidad", font=("Arial", 14, "bold")).grid(row=9, column=0, columnspan=2, pady=10)
        
        # Crear Treeview para la tabla
        self.tree = ttk.Treeview(self.resultados_frame, columns=("Estado", "P(n)", "P(Acum)"), show="headings")
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("P(n)", text="P(n)")
        self.tree.heading("P(Acum)", text="P(Acum)")
        self.tree.grid(row=10, column=0, columnspan=2, padx=10, pady=10)
        
        # Agregar barra de desplazamiento
        scrollbar = ttk.Scrollbar(self.resultados_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=10, column=2, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Llenar la tabla con los datos
        for i, (p_abs, p_acum) in enumerate(zip(self.resultados["probabilidades_absolutas"], self.resultados["probabilidades_acumuladas"])):
            self.tree.insert("", "end", values=(i, f"{p_abs:.4f}", f"{p_acum:.4f}"))
    
    def descargar_resultados(self):
        generar_reporte(self.resultados)
        messagebox.showinfo("Descarga completada", "Los resultados se han descargado en formato PDF.")
    
    def volver(self):
        self.destroy()  # Cierra esta ventana
        self.master.deiconify()  # Muestra la ventana principal

# Ejecutar la aplicación
if __name__ == "__main__":
    app = CalculadoraColas()
    app.mainloop()