import sys
import pygame

pygame.init()

# Configurações da tela
largura_tela = 800
altura_tela = 600
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Menu Principal")

# Cores
branco = (255, 255, 255)
preto = (0, 0, 0)

# Fonte
fonte = pygame.font.Font(None, 74)

def mostrar_menu():
    tela.fill(branco)
    titulo = fonte.render("Menu Principal", True, preto)
    opcao1 = fonte.render("Iniciar", True, preto)
    opcao2 = fonte.render("Configurações", True, preto)
    opcao3 = fonte.render("Sair", True, preto)

    tela.blit(titulo, (250, 100))
    tela.blit(opcao1, (250, 200))
    tela.blit(opcao2, (250, 300))
    tela.blit(opcao3, (250, 400))

    pygame.display.flip()

def main():
    while True:
        mostrar_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 250 <= x <= 550:
                    if 200 <= y <= 274:
                        print("Iniciando o jogo...")
                        # ...código para iniciar o jogo...
                    elif 300 <= y <= 374:
                        print("Abrindo configurações...")
                        # ...código para abrir configurações...
                    elif 400 <= y <= 474:
                        print("Saindo...")
                        pygame.quit()
                        sys.exit()

if __name__ == "__main__":
    main()
