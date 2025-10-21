import pygame
import random

pygame.init()

#Res y FPS
ANCHO = 400
ALTO = 600
FPS = 60

#Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AZUL = (100, 149, 237)
MARRON = (139, 69, 19)

player_image = pygame.image.load("player.png")
player_image = pygame.transform.scale(player_image, (40, 40))


jump_sound = pygame.mixer.Sound("jump_sound.mp3")  #Sonido al saltar

perdiste_sound = pygame.mixer.Sound("game_over_sound.mp3")  #Sonido al perder


nave_image = pygame.image.load("nave.png")
nave_image = pygame.transform.scale(nave_image, (40, 40))

#Cargar sonidos
pygame.mixer.music.load("background_music.mp3")  #Música de fondo
pygame.mixer.music.play(-1)  #Repetir indefinidamente la música de fondo
pygame.mixer.music.set_volume(50)

class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        
        self.rect = self.image.get_rect()
        self.rect.center = (ANCHO // 2, ALTO - 100)
        self.vel_y = 0
        self.vel_x = 0
        
    def update(self):
        #Movimiento horizontal
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        
        if keys[pygame.K_a]:
            self.vel_x = -6
        if keys[pygame.K_d]:
            self.vel_x = 6
            
        self.rect.x += self.vel_x
        
        #Wrap around (aparecer del otro lado)
        if self.rect.right < 0:
            self.rect.left = ANCHO
        if self.rect.left > ANCHO:
            self.rect.right = 0
            
        #Gravedad
        self.vel_y += 0.5
        self.rect.y += self.vel_y
        
    def saltar(self):
        self.vel_y = -15
        jump_sound.play()

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
        self.image = nave_image
        
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
        pygame.display.set_caption("Juego del Marcianito")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        self.fuente = pygame.font.Font(None, 36)
        self.fuente_chica = pygame.font.Font(None, 24)
        
        self.todos_sprites = pygame.sprite.Group()
        self.plataformas = pygame.sprite.Group()
        self.enemigos = pygame.sprite.Group()
        
        #Jugador
        self.jugador = Jugador()
        self.todos_sprites.add(self.jugador)
        
        #Variables de juego
        self.puntuacion = 0
        self.max_altura = 0
        self.desplazamiento_camara = 0
        self.dificultad = 1.0
        
        #Generar plataformas iniciales
        self.generar_plataformas_inicio()
        
    def generar_plataformas_inicio(self):
        #Plataforma inicial
        p = Plataforma(ANCHO // 2 - 30, ALTO - 60, "normal")
        self.plataformas.add(p)
        self.todos_sprites.add(p)
        
        #Generar plataformas hacia arriba
        for i in range(15):
            self.generar_plataforma()
    
    def generar_plataforma(self):
        #Calcular dificultad basada en la altura
        self.dificultad = 1.0 + (self.puntuacion // 1000) * 0.2
        
        x = random.randint(0, ANCHO - 60)
        
        if self.plataformas:
            #Buscar la plataforma más alta
            y_max = min([p.rect.y for p in self.plataformas])
            y = y_max - random.randint(50, int(100 / self.dificultad))
        else:
            y = ALTO - 100
        
        #Decidir tipo de plataforma según dificultad
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
        
        #Generar naves segun dificultad
        if self.puntuacion > 1000 and random.random() < 0.1 * self.dificultad:
            e = Enemigo(x, y - 40)
            self.enemigos.add(e)
            self.todos_sprites.add(e)
    
    def actualizar(self):
        self.todos_sprites.update()
        
        #Verificar colisiones con plataformas (solo cuando cae)
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
        
        #Verificar colisiones con enemigos
        if pygame.sprite.spritecollide(self.jugador, self.enemigos, False):
            self.game_over()
        
        #Mover cámara cuando el jugador sube
        if self.jugador.rect.top <= ALTO // 3:
            diferencia = ALTO // 3 - self.jugador.rect.top
            self.jugador.rect.y += diferencia
            self.desplazamiento_camara += diferencia
            
            #Mover todas las plataformas y enemigos
            for plataforma in self.plataformas:
                plataforma.rect.y += diferencia
                
            for enemigo in self.enemigos:
                enemigo.rect.y += diferencia
            
            #Act puntuación
            self.puntuacion = int(self.desplazamiento_camara)
            if self.puntuacion > self.max_altura:
                self.max_altura = self.puntuacion
        
        for plataforma in self.plataformas:
            if plataforma.rect.top > ALTO:
                plataforma.kill()
                
        for enemigo in self.enemigos:
            if enemigo.rect.top > ALTO:
                enemigo.kill()
        
        #Generar nuevas plataformas
        while len(self.plataformas) < 15:
            self.generar_plataforma()
        
        #Game Over si el jugador se cae
        if self.jugador.rect.top > ALTO:
            self.game_over()
    
    def dibujar(self):
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
        
        #Mostrar puntuación
        texto_puntuacion = self.fuente.render(
            f"Altura: {self.puntuacion}", True, NEGRO
        )
        self.pantalla.blit(texto_puntuacion, (10, 10))
        
        pygame.display.flip()
    
    def game_over(self):
        #Pantalla de Game Over
        perdiste_sound.play()
        
        self.pantalla.fill(NEGRO)
        

        texto_go = self.fuente.render("PERDISTE", True, ROJO)
        rect_go = texto_go.get_rect(center=(ANCHO // 2, ALTO // 2 - 50))
        self.pantalla.blit(texto_go, rect_go)
        
        texto_puntuacion = self.fuente_chica.render(
            f"Altura alcanzada: {self.puntuacion}", True, BLANCO
        )
        rect_puntuacion = texto_puntuacion.get_rect(
            center=(ANCHO // 2, ALTO // 2)
        )
        self.pantalla.blit(texto_puntuacion, rect_puntuacion)
        
        texto_reiniciar = self.fuente_chica.render(
            "ESPACIO para reiniciar", True, BLANCO
        )
        rect_reiniciar = texto_reiniciar.get_rect(
            center=(ANCHO // 2, ALTO // 2 + 50)
        )
        self.pantalla.blit(texto_reiniciar, rect_reiniciar)
        
        texto_salir = self.fuente_chica.render(
            "ESC para salir", True, BLANCO
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
                        self.__init__()  #Reset del juego
                    if evento.key == pygame.K_ESCAPE:
                        self.corriendo = False
                        esperando = False
    
    def ejecutar(self):
        while self.corriendo:
            self.reloj.tick(FPS)
            
            #Eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.corriendo = False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.corriendo = False
            
            self.actualizar()
            self.dibujar()
        
        pygame.quit()

if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()