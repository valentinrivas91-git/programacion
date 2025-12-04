import pygame, random, sys

pygame.init()
pygame.mixer.init()

# --- Configuración ---
ANCHO, ALTO, FPS = 500, 600, 60
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego Optimizado")
clock = pygame.time.Clock()

BLANCO = (255, 255, 255)
GRIS = (30, 30, 30)

fuente = pygame.font.SysFont(None, 32)
fuente_big = pygame.font.SysFont(None, 60)

skins = {
    "Azul": (0, 120, 255),
    "Verde": (0, 200, 120),
    "Naranja": (255, 140, 0),
    "Violeta": (160, 80, 200)
}

POWER_TYPES = ["shield", "slow", "double"]
POWER_DURATION = 4000


def texto_centrado(txt, y, f=fuente, color=BLANCO):
    r = f.render(txt, True, color)
    pantalla.blit(r, r.get_rect(center=(ANCHO // 2, y)))


# ===============================================================
#                          CLASE JUEGO
# ===============================================================
class Juego:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = ANCHO // 2 - 20
        self.y = ALTO - 70
        self.color = skins["Azul"]
        self.vel = 5

        self.obst = []
        self.powerups = []
        self.powers = {}
        self.vidas = 3
        self.puntaje = 0

        self.spawn_timer = 0
        self.spawn_rate = 400
        self.start_time = pygame.time.get_ticks()

    def spawn_obst(self):
        tipo = random.choices(
            ["normal", "big", "fast", "zigzag"],
            weights=[84, 4, 4, 4]
        )[0]

        size = random.randint(25, 40)
        if tipo == "big": size = random.randint(40, 70)
        vel = random.uniform(2.5, 4.5)
        if tipo == "fast": vel = random.uniform(4.5, 6.5)

        self.obst.append([random.randint(0, ANCHO - size), -size, size, vel, tipo, random.choice([-1, 1])])

    def spawn_power(self):
        t = random.choice(POWER_TYPES)
        self.powerups.append([random.randint(0, 470), -20, 20, t, 2])

    def update(self):
        t = pygame.time.get_ticks()

        # dificultad automática
        if t - self.spawn_timer > max(150, self.spawn_rate - (t - self.start_time) // 1000 * 2):
            self.spawn_obst()
            self.spawn_timer = t
            if random.random() < 0.08:
                self.spawn_power()

        # actualizar obstáculos
        slow = 0.6 if "slow" in self.powers else 1
        nuevos = []
        for o in self.obst:
            if o[4] == "zigzag":
                o[0] += o[5] * 1.5
                if o[0] <= 0 or o[0] >= ANCHO - o[2]: o[5] *= -1
            o[1] += o[3] * slow

            if o[1] > ALTO:
                self.puntaje += 10 * (2 if "double" in self.powers else 1)
            else:
                nuevos.append(o)
        self.obst = nuevos

        # powerups
        self.powerups = [p for p in self.powerups if p[1] < ALTO]
        for p in self.powerups:
            p[1] += p[4]

        # expirar powers
        self.powers = {k: v for k, v in self.powers.items() if v > t}

    def colisiones(self):
        pj = pygame.Rect(self.x, self.y, 40, 40)

        # power-ups
        for p in list(self.powerups):
            if pj.colliderect(pygame.Rect(p[0], p[1], p[2], p[2])):
                self.powers[p[3]] = pygame.time.get_ticks() + POWER_DURATION
                self.powerups.remove(p)

        # obstáculos
        for o in list(self.obst):
            if pj.colliderect(pygame.Rect(o[0], o[1], o[2], o[2])):
                if "shield" in self.powers:
                    del self.powers["shield"]
                    self.obst.remove(o)
                else:
                    self.vidas -= 1
                    self.obst.remove(o)
                    if self.vidas <= 0:
                        return False
        return True

    def dibujar(self):
        pantalla.fill(GRIS)

        pygame.draw.rect(pantalla, self.color, (self.x, self.y, 40, 40))

        for o in self.obst:
            pygame.draw.rect(pantalla, (200, 50, 50), (o[0], o[1], o[2], o[2]))

        for p in self.powerups:
            pygame.draw.ellipse(pantalla, (255, 215, 0), (p[0], p[1], p[2], p[2]))

        pantalla.blit(fuente.render(f"Vidas: {self.vidas}", True, BLANCO), (10, 10))
        pantalla.blit(fuente.render(f"Puntos: {self.puntaje}", True, BLANCO), (10, 40))


# ===============================================================
#                          MENÚ
# ===============================================================
def menu(juego):
    skins_list = list(skins.keys())
    i = 0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    juego.reset()
                    juego.color = skins[skins_list[i]]
                    return
                if e.key == pygame.K_UP: i = (i - 1) % len(skins_list)
                if e.key == pygame.K_DOWN: i = (i + 1) % len(skins_list)

        pantalla.fill(GRIS)
        texto_centrado("MENÚ PRINCIPAL", 80, fuente_big)
        texto_centrado("ENTER para jugar", 140)

        y = 240
        for n in skins_list:
            c = skins[n]
            marca = "→ " if n == skins_list[i] else "  "
            pantalla.blit(fuente.render(marca + n, True, c), (150, y))
            y += 40

        pygame.display.flip()
        clock.tick(FPS)


# ===============================================================
#                          GAME OVER
# ===============================================================
def gameover(juego):
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.K_RETURN: return

        pantalla.fill((0, 0, 0))
        texto_centrado("GAME OVER", 200, fuente_big, (255, 50, 50))
        texto_centrado(f"Puntaje: {juego.puntaje}", 260)
        texto_centrado("ENTER para volver al menú", 320)
        pygame.display.flip()
        clock.tick(FPS)


# ===============================================================
#                          BUCLE PRINCIPAL
# ===============================================================
def main():
    juego = Juego()

    while True:
        menu(juego)

        jugando = True
        while jugando:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                    pausa(juego)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: juego.x -= juego.vel
            if keys[pygame.K_RIGHT]: juego.x += juego.vel
            juego.x = max(0, min(ANCHO - 40, juego.x))

            juego.update()
            if not juego.colisiones():
                gameover(juego)
                break

            juego.dibujar()
            pygame.display.flip()
            clock.tick(FPS)


def pausa(juego):
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                return

        juego.dibujar()
        texto_centrado("PAUSA (P para seguir)", ALTO // 2, fuente_big)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()