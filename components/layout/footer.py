# Componente Footer con efecto marquesina
# Footer animado con texto deslizante de izquierda a derecha y viceversa

import customtkinter as ctk


class AnimatedFooter:
    """
    Footer animado con efecto marquesina
    Texto que se desplaza de izquierda a derecha y luego de derecha a izquierda
    """

    def __init__(self, parent):
        self.parent = parent
        self.text = "Multisoluciones IA -- La mejor solución para tus necesidades empresariales"

        # Configuración de la animación
        self.animation_speed = 50  # ms entre actualizaciones
        self.scroll_speed = 2  # píxeles por actualización
        self.direction = 1  # 1 = derecha, -1 = izquierda

        # Variables de posición
        self.text_x = 0
        self.text_width = 0
        self.canvas_width = 0

        # Estado de la animación
        self.animation_running = False
        self.animation_job = None

        self.create_footer()

    def create_footer(self):
        """Crea el footer con canvas para animación"""
        # Frame principal del footer
        self.footer_frame = ctk.CTkFrame(
            self.parent,
            height=50,
            fg_color="#2E86AB",
            corner_radius=0
        )
        self.footer_frame.pack(side="bottom", fill="x")
        self.footer_frame.pack_propagate(False)  # Mantener altura fija

        # Canvas para la animación del texto
        self.canvas = ctk.CTkCanvas(
            self.footer_frame,
            height=50,
            bg="#2E86AB",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # Configurar el texto inicial
        self.setup_text()

        # Iniciar animación
        self.start_animation()

        # Vincular eventos de redimensionamiento
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def setup_text(self):
        """Configura el texto en el canvas"""
        # Limpiar canvas
        self.canvas.delete("all")

        # Obtener dimensiones del canvas
        self.canvas.update()
        self.canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Crear texto en el canvas
        self.text_item = self.canvas.create_text(
            self.text_x,
            canvas_height // 2,
            text=self.text,
            fill="white",
            font=("Arial", 14, "bold"),
            anchor="w"
        )

        # Obtener ancho del texto
        text_bbox = self.canvas.bbox(self.text_item)
        if text_bbox:
            self.text_width = text_bbox[2] - text_bbox[0]

        # Posición inicial (empezar desde la izquierda)
        if self.text_x == 0 and self.canvas_width > 0:
            self.text_x = -self.text_width

    def animate_text(self):
        """Anima el movimiento del texto"""
        if not self.animation_running:
            return

        # Actualizar posición según la dirección
        self.text_x += self.scroll_speed * self.direction

        # Verificar límites y cambiar dirección
        if self.direction == 1:  # Moviéndose a la derecha
            if self.text_x > self.canvas_width:
                self.direction = -1  # Cambiar a izquierda
        else:  # Moviéndose a la izquierda
            if self.text_x + self.text_width < 0:
                self.direction = 1  # Cambiar a derecha

        # Actualizar posición del texto en el canvas
        canvas_height = self.canvas.winfo_height()
        self.canvas.coords(self.text_item, self.text_x, canvas_height // 2)

        # Programar siguiente actualización
        self.animation_job = self.parent.after(self.animation_speed, self.animate_text)

    def start_animation(self):
        """Inicia la animación"""
        if not self.animation_running:
            self.animation_running = True
            self.animate_text()

    def stop_animation(self):
        """Detiene la animación"""
        self.animation_running = False
        if self.animation_job:
            self.parent.after_cancel(self.animation_job)
            self.animation_job = None

    def on_canvas_resize(self, event):
        """Maneja el redimensionamiento del canvas"""
        # Actualizar ancho del canvas
        self.canvas_width = event.width

        # Reconfigurar texto si es necesario
        if hasattr(self, 'text_item'):
            canvas_height = self.canvas.winfo_height()
            self.canvas.coords(self.text_item, self.text_x, canvas_height // 2)

    def update_text(self, new_text):
        """Actualiza el texto del footer"""
        self.text = new_text
        self.setup_text()

    def set_animation_speed(self, speed_ms):
        """Configura la velocidad de animación"""
        self.animation_speed = max(10, min(200, speed_ms))

    def set_scroll_speed(self, speed_pixels):
        """Configura la velocidad de desplazamiento"""
        self.scroll_speed = max(1, min(10, speed_pixels))

    def get_widget(self):
        """Retorna el widget principal del footer"""
        return self.footer_frame

    def destroy(self):
        """Destruye el footer y limpia la animación"""
        self.stop_animation()
        self.footer_frame.destroy()


class SimpleFooter:
    """
    Footer simple sin animación (fallback)
    Para uso cuando se requiere menor uso de recursos
    """

    def __init__(self, parent):
        self.parent = parent
        self.text = "Multisoluciones IA -- La mejor solución para tus necesidades empresariales"
        self.create_footer()

    def create_footer(self):
        """Crea un footer simple"""
        self.footer_frame = ctk.CTkFrame(
            self.parent,
            height=50,
            fg_color="#2E86AB",
            corner_radius=0
        )
        self.footer_frame.pack(side="bottom", fill="x")

        # Texto centrado
        self.footer_label = ctk.CTkLabel(
            self.footer_frame,
            text=self.text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
            fg_color="transparent"
        )
        self.footer_label.pack(expand=True, pady=15)

    def update_text(self, new_text):
        """Actualiza el texto del footer"""
        self.text = new_text
        self.footer_label.configure(text=new_text)

    def get_widget(self):
        """Retorna el widget principal del footer"""
        return self.footer_frame

    def destroy(self):
        """Destruye el footer"""
        self.footer_frame.destroy()