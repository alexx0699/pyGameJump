import pygame
import random
import math

# Inicializar Pygame
pygame.init()

# Constantes
ANCHO = 400
ALTO = 600
FPS = 60

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AZUL = (100, 149, 237)
MARRON = (139, 69, 19)

class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.ancho = 40
        self.alto = 40
        self.image = pygame.Surface((self.ancho, self.alto))
        self.image.fill(VERDE)
        # Dibujar cara simple
        pygame.draw.circle(self.image, NEGRO, (12, 15), 3)
        pygame.draw.circle(self.image, NEGRO, (28, 15), 3)
        pygame.draw.arc(self.image, NEGRO, (10, 20, 20, 10), 0, math.pi, 2)
        
        self.rect = self.image.get_rect()
        self.rect.center = (ANCHO // 2, ALTO - 100)
        self.vel_y = 0
        self.vel_x = 0
        
    def update(self):
        # Movimiento horizontal
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        
        if keys[pygame.K_a]:
            self.vel_x = -6
        if keys[pygame.K_d]:
            self.vel_x = 6
            
        self.rect.x += self.vel_x
        
        # Wrap around (aparecer del otro lado)
        if self.rect.right < 0:
            self.rect.left = ANCHO
        if self.rect.left > ANCHO:
            self.rect.right = 0
            
        # Gravedad
        self.vel_y += 0.5
        self.rect.y += self.vel_y
        
    def saltar(self):
        self.vel_y = -15

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo="normal"):
        super().__init__()
        self.ancho = 60
        self.alto = 10
        self.tipo = tipo
        self.image = pygame.Surface((self.ancho, self.alto))
        
        if tipo == "normal":
            self.image.fill(MARRON)
        elif tipo == "movil":
            self.image.fill(AZUL)
            self.vel_x = random.choice([-2, 2])
        elif tipo == "fragil":
            self.image.fill(ROJO)
            self.rota = False
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def update(self):
        if self.tipo == "movil":
            self.rect.x += self.vel_x
            if self.rect.right > ANCHO or self.rect.left < 0:
                self.vel_x *= -1

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.ancho = 30
        self.alto = 30
        self.image = pygame.Surface((self.ancho, self.alto))
        self.image.fill(ROJO)
        # Dibujar cara enemiga
        pygame.draw.circle(self.image, NEGRO, (10, 12), 2)
        pygame.draw.circle(self.image, NEGRO, (20, 12), 2)
        pygame.draw.line(self.image, NEGRO, (8, 22), (22, 22), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = random.choice([-1.5, 1.5])
        
    def update(self):
        self.rect.x += self.vel_x
        if self.rect.right > ANCHO or self.rect.left < 0:
            self.vel_x *= -1

class Juego:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Doodle Jump")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        self.fuente = pygame.font.Font(None, 36)
        self.fuente_pequena = pygame.font.Font(None, 24)
        
        # Grupos de sprites
        self.todos_sprites = pygame.sprite.Group()
        self.plataformas = pygame.sprite.Group()
        self.enemigos = pygame.sprite.Group()
        
        # Jugador
        self.jugador = Jugador()
        self.todos_sprites.add(self.jugador)
        
        # Variables de juego
        self.puntuacion = 0
        self.max_altura = 0
        self.desplazamiento_camara = 0
        self.dificultad = 1.0
        
        # Generar plataformas iniciales
        self.generar_plataformas_iniciales()
        
    def generar_plataformas_iniciales(self):
        # Plataforma inicial
        p = Plataforma(ANCHO // 2 - 30, ALTO - 60, "normal")
        self.plataformas.add(p)
        self.todos_sprites.add(p)
        
        # Generar plataformas hacia arriba
        for i in range(15):
            self.generar_plataforma()
    
    def generar_plataforma(self):
        # Calcular dificultad basada en la altura
        self.dificultad = 1.0 + (self.puntuacion // 1000) * 0.2
        
        x = random.randint(0, ANCHO - 60)
        
        if self.plataformas:
            # Buscar la plataforma más alta
            y_max = min([p.rect.y for p in self.plataformas])
            y = y_max - random.randint(50, int(100 / self.dificultad))
        else:
            y = ALTO - 100
        
        # Decidir tipo de plataforma según dificultad
        rand = random.random()
        
        if self.puntuacion < 500:
            tipo = "normal"
        elif rand < 0.7:
            tipo = "normal"
        elif rand < 0.85:
            tipo = "movil"
        else:
            tipo = "fragil"
            
        p = Plataforma(x, y, tipo)
        self.plataformas.add(p)
        self.todos_sprites.add(p)
        
        # Generar enemigos con probabilidad según dificultad
        if self.puntuacion > 1000 and random.random() < 0.1 * self.dificultad:
            e = Enemigo(x, y - 40)
            self.enemigos.add(e)
            self.todos_sprites.add(e)
    
    def actualizar(self):
        self.todos_sprites.update()
        
        # Verificar colisiones con plataformas (solo cuando cae)
        if self.jugador.vel_y > 0:
            colisiones = pygame.sprite.spritecollide(
                self.jugador, self.plataformas, False
            )
            for plataforma in colisiones:
                if self.jugador.rect.bottom < plataforma.rect.bottom:
                    if plataforma.tipo == "fragil":
                        if not plataforma.rota:
                            plataforma.rota = True
                            plataforma.kill()
                    else:
                        self.jugador.rect.bottom = plataforma.rect.top
                        self.jugador.saltar()
        
        # Verificar colisiones con enemigos
        if pygame.sprite.spritecollide(self.jugador, self.enemigos, False):
            self.game_over()
        
        # Mover cámara cuando el jugador sube
        if self.jugador.rect.top <= ALTO // 3:
            diferencia = ALTO // 3 - self.jugador.rect.top
            self.jugador.rect.y += diferencia
            self.desplazamiento_camara += diferencia
            
            # Mover todas las plataformas y enemigos hacia abajo
            for plataforma in self.plataformas:
                plataforma.rect.y += diferencia
                
            for enemigo in self.enemigos:
                enemigo.rect.y += diferencia
            
            # Actualizar puntuación
            self.puntuacion = int(self.desplazamiento_camara)
            if self.puntuacion > self.max_altura:
                self.max_altura = self.puntuacion
        
        # Eliminar plataformas y enemigos fuera de pantalla
        for plataforma in self.plataformas:
            if plataforma.rect.top > ALTO:
                plataforma.kill()
                
        for enemigo in self.enemigos:
            if enemigo.rect.top > ALTO:
                enemigo.kill()
        
        # Generar nuevas plataformas
        while len(self.plataformas) < 15:
            self.generar_plataforma()
        
        # Game Over si el jugador cae
        if self.jugador.rect.top > ALTO:
            self.game_over()
    
    def dibujar(self):
        # Fondo degradado
        for y in range(ALTO):
            color_r = 135 + int((y / ALTO) * 70)
            color_g = 206 + int((y / ALTO) * 49)
            color_b = 235 + int((y / ALTO) * 20)
            pygame.draw.line(
                self.pantalla, 
                (color_r, color_g, color_b), 
                (0, y), 
                (ANCHO, y)
            )
        
        self.todos_sprites.draw(self.pantalla)
        
        # Mostrar puntuación
        texto_puntuacion = self.fuente.render(
            f"Altura: {self.puntuacion}", True, NEGRO
        )
        self.pantalla.blit(texto_puntuacion, (10, 10))
        
        # Mostrar controles
        texto_controles = self.fuente_pequena.render(
            "A/D para mover", True, NEGRO
        )
        self.pantalla.blit(texto_controles, (10, 50))
        
        # Mostrar dificultad
        texto_dificultad = self.fuente_pequena.render(
            f"Dificultad: {self.dificultad:.1f}x", True, NEGRO
        )
        self.pantalla.blit(texto_dificultad, (10, 75))
        
        pygame.display.flip()
    
    def game_over(self):
        # Pantalla de Game Over
        self.pantalla.fill(NEGRO)
        
        texto_go = self.fuente.render("GAME OVER", True, ROJO)
        rect_go = texto_go.get_rect(center=(ANCHO // 2, ALTO // 2 - 50))
        self.pantalla.blit(texto_go, rect_go)
        
        texto_puntuacion = self.fuente_pequena.render(
            f"Altura alcanzada: {self.puntuacion}", True, BLANCO
        )
        rect_puntuacion = texto_puntuacion.get_rect(
            center=(ANCHO // 2, ALTO // 2)
        )
        self.pantalla.blit(texto_puntuacion, rect_puntuacion)
        
        texto_reiniciar = self.fuente_pequena.render(
            "Presiona ESPACIO para reiniciar", True, BLANCO
        )
        rect_reiniciar = texto_reiniciar.get_rect(
            center=(ANCHO // 2, ALTO // 2 + 50)
        )
        self.pantalla.blit(texto_reiniciar, rect_reiniciar)
        
        texto_salir = self.fuente_pequena.render(
            "Presiona ESC para salir", True, BLANCO
        )
        rect_salir = texto_salir.get_rect(
            center=(ANCHO // 2, ALTO // 2 + 80)
        )
        self.pantalla.blit(texto_salir, rect_salir)
        
        pygame.display.flip()
        
        esperando = True
        while esperando:
            self.reloj.tick(FPS)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.corriendo = False
                    esperando = False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        esperando = False
                        self.__init__()  # Reiniciar juego
                    if evento.key == pygame.K_ESCAPE:
                        self.corriendo = False
                        esperando = False
    
    def ejecutar(self):
        while self.corriendo:
            self.reloj.tick(FPS)
            
            # Eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.corriendo = False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.corriendo = False
            
            self.actualizar()
            self.dibujar()
        
        pygame.quit()

# Ejecutar el juego
if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()