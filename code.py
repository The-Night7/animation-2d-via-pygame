import pygame
import sys
import math
import random
import os
import time

# --- Initialisation de Pygame ---
pygame.init()
pygame.mixer.init()

# Configuration de la fenêtre
LARGEUR, HAUTEUR = 1000, 700
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Animation : Legendary - EPIC The Musical")
horloge = pygame.time.Clock()

# Couleurs
NOIR = (10, 10, 15)
BLANC = (255, 255, 255)
BLEU_TELEMACHUS = (50, 150, 255)
ROUGE_MONSTRE = (255, 50, 50)
OR_LEGENDAIRE = (255, 215, 0)
VIOLET_SOMBRE = (40, 0, 60)

# Polices
try:
    police_titre = pygame.font.SysFont("georgia", 48, bold=True)
    police_texte = pygame.font.SysFont("georgia", 32, italic=True)
except:
    police_titre = pygame.font.Font(None, 48)
    police_texte = pygame.font.Font(None, 32)

# --- Synchronisation : Timestamps et paroles ---
# Basé sur la vidéo YouTube "Legendary | EPIC: The Musical Animatic"
evenements_paroles = [
    (0.0, ""),
    (16.0, "It's just me myself and I..."),
    (20.0, "Stuck in my bedroom living in this world you left behind"),
    (25.0, "Dreaming of all these monsters that I'll never get to fight"),
    (33.0, "Cuz I'm stuck with your stories but no clue who you are"),
    (42.0, "Somebody tell me... Come and give me a sign"),
    (53.0, "Give me sirens and a cyclops!"),
    (58.0, "Give me giants and a hydra!"),
    (62.0, "I want to be LEGENDARY!"),
    (81.0, "108 old faces who call me small..."),
    (102.0, "Somebody help me... Come and give me the strength"),
    (112.0, "Give me sirens and a cyclops!"),
    (116.0, "Give me giants and a hydra!"),
    (122.0, "I want to be LEGENDARY!"),
    (138.0, "Where is he? Where is the man who loved you?"),
    (164.0, "Don't you dare call my mother a tramp!"),
    (174.0, "Somebody tell me... come and give me a sign!"),
    (195.0, "It's just me myself and I..."),
    (230.0, "...")  # Fin
]


# --- Classes pour les effets visuels ---
class Particule:
    def __init__(self, x, y, couleur, vitesse_x, vitesse_y, duree_vie, taille_init):
        self.x = x
        self.y = y
        self.couleur = couleur
        self.vitesse_x = vitesse_x
        self.vitesse_y = vitesse_y
        self.duree_vie = duree_vie
        self.age = 0
        self.taille = taille_init

    def mettre_a_jour(self):
        self.x += self.vitesse_x
        self.y += self.vitesse_y
        self.age += 1
        # Diminue la taille avec le temps
        if self.taille > 0.1:
            self.taille -= self.taille / self.duree_vie

    def dessiner(self, surface):
        if self.age < self.duree_vie:
            alpha = max(0, 255 - int((self.age / self.duree_vie) * 255))
            surf_particule = pygame.Surface((int(self.taille * 2), int(self.taille * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf_particule, (*self.couleur, alpha), (int(self.taille), int(self.taille)),
                               int(self.taille))
            surface.blit(surf_particule, (int(self.x - self.taille), int(self.y - self.taille)))


def generer_explosion(x, y, couleur, nombre=50, vitesse_max=8, taille_max=8):
    particules = []
    for _ in range(nombre):
        angle = random.uniform(0, 2 * math.pi)
        vitesse = random.uniform(2, vitesse_max)
        vx = math.cos(angle) * vitesse
        vy = math.sin(angle) * vitesse
        duree = random.randint(30, 90)
        taille = random.randint(3, taille_max)
        particules.append(Particule(x, y, couleur, vx, vy, duree, taille))
    return particules


def main():
    # --- Chargement de la musique ---
    fichier_musique = "legendary.mp3"

    if os.path.exists(fichier_musique):
        try:
            pygame.mixer.music.load(fichier_musique)
            pygame.mixer.music.play()
            print("▶️ Musique lancée !")
        except Exception as e:
            print(f"Erreur lors du chargement de la musique : {e}")
    else:
        print(f"⚠️ ATTENTION : Le fichier '{fichier_musique}' est introuvable.")
        print("💡 L'animation se lancera sans le son.")
        print("👉 Placez un fichier nommé 'legendary.mp3' dans le même dossier que ce script pour activer l'audio.")

    en_cours = True
    temps_debut = time.time()

    particules = []
    index_parole_actuelle = 0
    texte_actuel = ""
    intensite_fond = 0
    tremblement = 0

    centre_x, centre_y = LARGEUR // 2, HAUTEUR // 2

    while en_cours:
        temps_ecoule = time.time() - temps_debut

        # Gestion de la fermeture de la fenêtre
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    en_cours = False

        # --- Logique de Synchronisation ---
        if index_parole_actuelle < len(evenements_paroles) - 1:
            prochain_temps = evenements_paroles[index_parole_actuelle + 1][0]
            if temps_ecoule >= prochain_temps:
                index_parole_actuelle += 1
                texte_actuel = evenements_paroles[index_parole_actuelle][1]

                # Déclenchement d'effets visuels selon les mots clés
                texte_min = texte_actuel.lower()
                if "cyclops" in texte_min or "hydra" in texte_min or "monsters" in texte_min:
                    # Apparition des monstres (explosions rouges sur les bords)
                    particules.extend(
                        generer_explosion(random.randint(50, LARGEUR - 50), random.randint(50, HAUTEUR - 50),
                                          ROUGE_MONSTRE, 150, 12, 15))
                    intensite_fond = 80
                    tremblement = 10
                elif "legendary" in texte_min:
                    # Moment épique : Énorme explosion dorée au centre
                    particules.extend(generer_explosion(centre_x, centre_y, OR_LEGENDAIRE, 300, 20, 20))
                    intensite_fond = 150
                    tremblement = 20

        # Réduction progressive des effets (Tremblement de caméra et flash d'arrière plan)
        if intensite_fond > 0: intensite_fond -= 3
        if tremblement > 0: tremblement -= 1

        offset_x = random.randint(-tremblement, tremblement) if tremblement > 0 else 0
        offset_y = random.randint(-tremblement, tremblement) if tremblement > 0 else 0

        # Pulsation de la musique simulée par un sinus mathématique
        battement = math.sin(temps_ecoule * 4) * 10
        rayon_perso = 40 + battement if temps_ecoule > 16 else 30

        # --- Rendu Graphique ---
        # Dessin du fond qui flashe
        couleur_fond = (min(255, NOIR[0] + intensite_fond), NOIR[1], NOIR[2])
        ecran.fill(couleur_fond)

        # Dessin de l'aura de Telemachus (le héros au centre)
        surf_aura = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.circle(surf_aura, (*BLEU_TELEMACHUS, 60), (100, 100), int(rayon_perso + 25))
        ecran.blit(surf_aura, (centre_x - 100 + offset_x, centre_y - 100 + offset_y))

        # Dessin du "héros"
        pygame.draw.circle(ecran, BLANC, (centre_x + offset_x, centre_y + offset_y), int(rayon_perso))
        pygame.draw.circle(ecran, BLEU_TELEMACHUS, (centre_x + offset_x, centre_y + offset_y), int(rayon_perso - 5))

        # Mise à jour et dessin des particules
        particules_restantes = []
        for p in particules:
            p.mettre_a_jour()
            p.dessiner(ecran)
            if p.age < p.duree_vie:
                particules_restantes.append(p)
        particules = particules_restantes

        # Affichage des Paroles (Sous-titres)
        if texte_actuel:
            rendu_texte = police_texte.render(texte_actuel, True, BLANC)
            rect_texte = rendu_texte.get_rect(center=(LARGEUR // 2, HAUTEUR - 100))

            # Fond sombre pour bien lire les paroles
            padding = 15
            rect_fond = pygame.Rect(rect_texte.left - padding, rect_texte.top - padding, rect_texte.width + padding * 2,
                                    rect_texte.height + padding * 2)

            surf_fond_texte = pygame.Surface((rect_fond.width, rect_fond.height), pygame.SRCALPHA)
            pygame.draw.rect(surf_fond_texte, (0, 0, 0, 180), surf_fond_texte.get_rect(), border_radius=15)
            ecran.blit(surf_fond_texte, (rect_fond.x, rect_fond.y))
            ecran.blit(rendu_texte, rect_texte)

        # Affichage du chronomètre (utile pour vérifier la synchronisation)
        texte_timer = pygame.font.Font(None, 24).render(f"Temps: {temps_ecoule:.1f}s", True, (150, 150, 150))
        ecran.blit(texte_timer, (10, 10))

        # Rafraîchissement de l'écran
        pygame.display.flip()
        horloge.tick(60)  # Limité à 60 FPS

    # Fermeture propre
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()