import pygame
import os
import random

# Dimensões da tela
TELA_LARGURA = 500
TELA_ALTURA = 800

# Configurações do jogo
FPS = 30
IMAGEM_CANO = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "pipe.png"))
)
IMAGEM_CHAO = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "base.png"))
)
IMAGEM_BACKGROUND = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "bg.png"))
)
IMAGEM_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png"))),
]

# Fonte para exibir a pontuação
pygame.font.init()
FONTE_PONTO = pygame.font.SysFont("arial", 30)
FONTE_GAME_OVER = pygame.font.SysFont("arial", 60, bold=True)
FONTE_MENU = pygame.font.SysFont("arial", 40, bold=True)
FONTE_TITLE = pygame.font.SysFont("arial", 45, bold=True)


# Classe Pássaro
class Passaro:
    IMGS = IMAGEM_PASSARO
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[1]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        self.contagem_imagem += 1
        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4:
            self.imagem = self.IMGS[1]
        else:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO * 2

        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


# Classe Cano
class Cano:
    DISTANCIA = 200
    VELOCIDADE = 5
    GRAVIDADE = 1
    FORCA_PULO = -12

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.offset = 0
        self.vel_y = 0
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self, invertido=False):
        self.x -= self.VELOCIDADE
        if invertido:
            self.vel_y += self.GRAVIDADE
            self.offset += self.vel_y

            if self.offset > 250:
                self.offset = 250
                self.vel_y = 0
            if self.offset < -250:
                self.offset = -250
                self.vel_y = 0

    def pular(self):
        self.vel_y = self.FORCA_PULO

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo + self.offset))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base + self.offset))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (
            self.x - passaro.x,
            self.pos_topo + self.offset - round(passaro.y),
        )
        distancia_base = (
            self.x - passaro.x,
            self.pos_base + self.offset - round(passaro.y),
        )

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        return bool(topo_ponto or base_ponto)


# Classe Chao
class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


# Função para desenhar tudo
def desenhar_tela(tela, passaros, canos, chao, pontos, modo):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))

    for cano in canos:
        cano.desenhar(tela)
    for passaro in passaros:
        passaro.desenhar(tela)

    texto = FONTE_PONTO.render(f"Pontos: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))

    chao.desenhar(tela)

    texto_modo = FONTE_PONTO.render(f"Modo: {modo}", 1, (255, 255, 0))
    tela.blit(texto_modo, (10, 10))

    pygame.display.update()


# Tela de Game Over
def game_over(tela, pontos, modo):
    texto_game_over = FONTE_GAME_OVER.render("GAME OVER", 1, (255, 0, 0))
    texto_restart = FONTE_PONTO.render("Pressione R", 1, (255, 255, 255))

    tela.blit(
        texto_game_over, (TELA_LARGURA / 2 - texto_game_over.get_width() / 2, 200)
    )
    tela.blit(texto_restart, (TELA_LARGURA / 2 - texto_restart.get_width() / 2, 300))

    pygame.display.update()

    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    esperando = False


# Menu de seleção de dificuldade
def menu():
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    opcoes = ["Normal", "Invertido"]
    selecionado = 0

    rodando = True
    while rodando:
        tela.blit(IMAGEM_BACKGROUND, (0, 0))

        titulo = FONTE_TITLE.render("PYTHONBIRD", 1, (255, 255, 255))
        tela.blit(titulo, (TELA_LARGURA / 2 - titulo.get_width() / 2, 100))

        for i, opcao in enumerate(opcoes):
            cor = (255, 255, 0) if i == selecionado else (255, 255, 255)
            texto = FONTE_MENU.render(opcao, 1, cor)
            tela.blit(texto, (TELA_LARGURA / 2 - texto.get_width() / 2, 200 + i * 60))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    selecionado = (selecionado - 1) % len(opcoes)
                elif evento.key == pygame.K_DOWN:
                    selecionado = (selecionado + 1) % len(opcoes)
                elif evento.key == pygame.K_RETURN:
                    return opcoes[selecionado]


# Função principal
def main(modo):
    passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()

    rodando = True
    while rodando:
        relogio.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    if modo == "Normal":
                        for passaro in passaros:
                            passaro.pular()
                    else:  # Invertido
                        for cano in canos:
                            cano.pular()

        if modo == "Normal":
            for passaro in passaros:
                passaro.mover()
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            cano.mover(modo == "Invertido")
            for passaro in passaros:
                if cano.colidir(passaro):
                    game_over(tela, pontos, modo)
                    return
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))

        for cano in remover_canos:
            canos.remove(cano)

        for passaro in passaros:
            if modo == "Normal":
                if passaro.y + passaro.imagem.get_height() > chao.y or passaro.y < 0:
                    game_over(tela, pontos, modo)
                    return

        desenhar_tela(tela, passaros, canos, chao, pontos, modo)


if __name__ == "__main__":
    while True:
        modo = menu()
        main(modo)
