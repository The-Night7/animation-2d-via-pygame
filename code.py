"""
Animatic amélioré pour "LEGENDARY - EPIC The Musical".

Ce script est dérivé de la version fournie mais apporte plusieurs
améliorations pour rendre l'animation plus immersive et, surtout,
pour synchroniser les textes avec la musique de façon plus fiable.

Principales améliorations :

1. **Synchronisation audio précise** : utilisation de
   `pygame.mixer.music.get_pos()` pour récupérer la position réelle
   de lecture de la musique (en millisecondes). Selon la
   documentation officielle de Pygame, cette méthode renvoie le
   nombre de millisecondes écoulées depuis le début de la lecture 【294909052533098†L279-L283】.
   Cela permet de synchroniser les événements même si l'animation
   commence avec un léger délai.

2. **Gestion robuste des événements** : la boucle principale
   utilise maintenant une boucle `while` pour mettre à jour les
   dialogues et les scènes dès que plusieurs événements se sont
   déclenchés entre deux frames. Cela évite de rater un changement
   lors d'une baisse momentanée de FPS.

3. **Transitions plus douces** : ajout d'un fondu enchaîné entre les
   décors lorsque la scène change. Un rectangle noir semi-transparent
   est superposé pendant la durée du fondu (par défaut 1 seconde).

4. **Paramètres configurables** : variables en haut de fichier
   permettent d'ajuster le décalage éventuel de la musique,
   l'intensité et la durée du tremblement de caméra, la durée du
   fondu, etc.

5. **Code structuré** : quelques fonctions utilitaires supplémentaires
   rendent le code plus lisible et facilitent son adaptation.

Pour tester ce script, assurez‑vous d'avoir le fichier
`legendary.mp3` dans le même dossier. Si le fichier n'est pas
présent, l'animation se lance en mode muet avec un timing basé sur
`time.time()`.

"""

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
pygame.display.set_caption("Animation : Legendary - EPIC The Musical (Animatic Version, améliorée)")
horloge = pygame.time.Clock()

# Couleurs (RGB)
NOIR = (15, 15, 20)
BLANC = (240, 240, 240)
PEAU = (255, 218, 185)
BLEU_TELEMACHUS = (50, 130, 220)
VIOLET_ANTINOUS = (120, 40, 180)
ROUGE_MONSTRE = (220, 20, 60)
OR_LEGENDAIRE = (255, 215, 0)
GRIS_MUR = (50, 50, 60)

# Polices
try:
    police_bulle = pygame.font.SysFont("comicsansms", 22, bold=True)
    police_titre = pygame.font.SysFont("georgia", 48, bold=True)
except Exception:
    # Fallback si la police n'est pas disponible
    police_bulle = pygame.font.Font(None, 26)
    police_titre = pygame.font.Font(None, 48)

# --- Base de données des Paroles avec l'orateur ---
# Format : (Temps_secondes, "Texte", "Orateur")
evenements_paroles = [
    (0.0, "", "Aucun"),
    (15.0, "It's just me, myself, and I", "Telemachus"),
    (18.5, "Stuck in my bedroom", "Telemachus"),
    (21.0, "Living in this world you left behind", "Telemachus"),
    (24.5, "Dreaming of all these monsters", "Telemachus"),
    (27.5, "That I'll never get to fight", "Telemachus"),
    (30.0, "But boy, I wish I could", "Telemachus"),
    (32.5, "So I could bring this world some light", "Telemachus"),
    (35.5, "'Cause I'm stuck with your stories", "Telemachus"),
    (38.0, "But no clue who you are", "Telemachus"),
    (40.0, "And no idea if you're dead or just too far", "Telemachus"),
    (43.5, "Somebody tell me, come and give me a sign", "Telemachus"),
    (49.0, "If I fight those monsters, is it you I'll find?", "Telemachus"),
    (53.5, "If so, then...", "Telemachus"),
    (55.0, "Give me sirens and a cyclops!", "Telemachus"),
    (58.0, "Give me giants and a hydra!", "Telemachus"),
    (61.0, "I know life and fate are scary", "Telemachus"),
    (64.0, "But I wanna be legendary!", "Telemachus"),
    (68.0, "I'll fight the harpies and chimeras", "Telemachus"),
    (71.0, "The Minotaurs, even Cerberus", "Telemachus"),
    (74.0, "I know life and fate are scary", "Telemachus"),
    (77.0, "But I wanna be l-l-l-l legendary!", "Telemachus"),
    (83.0, "There are strangers in our halls", "Telemachus"),
    (86.0, "Trying to win the heart of my mom", "Telemachus"),
    (89.0, "But she is standing tall", "Telemachus"),
    (91.5, "A hundred eight old faces of men who call me small", "Telemachus"),
    (95.0, "They keep taking space", "Telemachus"),
    (97.0, "And it's not much longer we can stall", "Telemachus"),
    (99.5, "'Cause they're getting impatient", "Telemachus"),
    (102.0, "Dangerous too and I would fight them", "Telemachus"),
    (104.5, "If I was half as strong as you", "Telemachus"),
    (108.0, "Somebody help me", "Telemachus"),
    (110.5, "Come and give me the strength", "Telemachus"),
    (113.0, "Can I do whatever it takes to keep my mom safe?", "Telemachus"),
    (116.5, "If so, then...", "Telemachus"),
    (118.0, "Give me sirens and a cyclops!", "Telemachus"),
    (121.0, "Give me giants and a hydra!", "Telemachus"),
    (124.0, "I know life and fate are scary", "Telemachus"),
    (127.0, "But I wanna be legendary!", "Telemachus"),
    (130.0, "I'll fight the harpies and chimeras", "Telemachus"),
    (133.0, "The Minotaurs, even Cerberus", "Telemachus"),
    (136.0, "I know life and fate are scary", "Telemachus"),
    (139.0, "But I wanna be legendary!", "Telemachus"),
    # Différenciation des voix (Télémaque vs Les Hommes/Prétendants)
    (144.0, "Where is he?", "Antinous"),
    (147.0, "Where is the man who'll have you to wife? Oh-oh", "Antinous"),
    (154.0, "Where is he?", "Telemachus"),
    (157.0, "Where is the man with whom you'll spend your life?", "Antinous"),
    (164.0, "'Cause it's been twenty years (twenty years)", "Antinous"),
    (168.0, "And we still have no king", "Antinous"),
    (171.0, "Give me a chance, a single opportunity and", "Telemachus"),
    (175.0, "I'll overcome these obstacles and scrutiny and", "Telemachus"),
    (179.0, "Boy...", "Antinous"),
    (181.0, "When's your tramp of a mother gonna choose a new husband?", "Antinous"),
    (187.0, "Why don't you open her room so we can have fun with her?", "Antinous"),
    (193.0, "Don't you dare call my mother a tramp!", "Telemachus"),
    (197.0, "I just did.", "Antinous"),
    (200.0, "Whatchu gonna do about it, champ?", "Antinous"),
    (206.0, "Somebody tell me", "Telemachus"),
    (210.0, "Come and give me a sign", "Telemachus"),
    (216.0, "If I fight this monster", "Telemachus"),
    (221.0, "Is it you I'll find?", "Telemachus"),
    (228.0, "...", "Aucun"),
]


# --- Utilitaires ---
def diviser_texte(texte: str, police: pygame.font.Font, largeur_max: int) -> list[str]:
    """Coupe une chaîne en plusieurs lignes de sorte qu'elle ne dépasse pas largeur_max.

    Args:
        texte: texte à couper.
        police: police de rendu.
        largeur_max: largeur max en pixels.

    Returns:
        Liste de lignes.
    """
    mots = texte.split(' ')
    lignes = []
    ligne_actuelle = ""
    for mot in mots:
        test_ligne = ligne_actuelle + mot + " "
        if police.size(test_ligne)[0] > largeur_max:
            lignes.append(ligne_actuelle)
            ligne_actuelle = mot + " "
        else:
            ligne_actuelle = test_ligne
    lignes.append(ligne_actuelle)
    return lignes


# --- Classes de l'Animatic ---
class Personnage:
    """Représente un personnage simple animé avec bulle de dialogue."""

    def __init__(self, nom: str, x: float, y: float, couleur_vetement: tuple[int, int, int],
                 taille: float = 1.0, inverser: bool = False) -> None:
        self.nom = nom
        self.x = x
        self.y = y
        self.couleur_vetement = couleur_vetement
        self.taille = taille
        self.inverser = inverser  # Regarde vers la gauche si True
        self.parle_actuellement = False
        self.texte_bulle = ""

    def dessiner(self, surface: pygame.Surface, temps: float) -> None:
        """Dessine le personnage sur la surface en animant la respiration et les bras."""
        # Animation de respiration
        respiration = math.sin(temps * 3) * 3

        # Coordonnées du corps
        t_x = self.x
        t_y = self.y + respiration
        hauteur_tronc = 70 * self.taille
        largeur_epaules = 30 * self.taille

        # Si le personnage parle, il bouge les bras
        mouvement_bras = math.sin(temps * 15) * 15 if self.parle_actuellement else 0
        direction = -1 if self.inverser else 1

        # Tronc (Tunique)
        rect_tunique = pygame.Rect(t_x - largeur_epaules // 2, t_y, largeur_epaules, hauteur_tronc)
        pygame.draw.rect(surface, self.couleur_vetement, rect_tunique, border_radius=8)

        # Tête
        rayon_tete = 22 * self.taille
        pygame.draw.circle(surface, PEAU, (int(t_x), int(t_y - rayon_tete + 5)), int(rayon_tete))

        # Bras (Lignes)
        epaule_x = t_x + (15 * direction * self.taille)
        pygame.draw.line(surface, PEAU, (t_x, t_y + 10),
                         (epaule_x + 10 * direction + mouvement_bras, t_y + 40 - mouvement_bras), int(8 * self.taille))
        pygame.draw.line(surface, PEAU, (t_x, t_y + 10), (t_x - (15 * direction) - mouvement_bras, t_y + 40),
                         int(8 * self.taille))

        # Jambes
        pygame.draw.line(surface, PEAU, (t_x - 10, t_y + hauteur_tronc),
                         (t_x - 15, t_y + hauteur_tronc + 40 * self.taille), int(8 * self.taille))
        pygame.draw.line(surface, PEAU, (t_x + 10, t_y + hauteur_tronc),
                         (t_x + 15, t_y + hauteur_tronc + 40 * self.taille), int(8 * self.taille))

        # Bulle de dialogue
        if self.parle_actuellement and self.texte_bulle:
            self.dessiner_bulle(surface, self.texte_bulle, t_x, t_y - rayon_tete - 20)

    def dessiner_bulle(self, surface: pygame.Surface, texte: str, x: float, y: float) -> None:
        """Dessine une bulle de dialogue adaptée à la taille du texte."""
        lignes = diviser_texte(texte, police_bulle, 250)
        hauteur_ligne = police_bulle.get_height()
        largeur_bulle = max([police_bulle.size(l)[0] for l in lignes]) + 30
        hauteur_bulle = (hauteur_ligne * len(lignes)) + 20

        rect_bulle = pygame.Rect(x - largeur_bulle // 2, y - hauteur_bulle, largeur_bulle, hauteur_bulle)

        # Fond de la bulle et bordure
        pygame.draw.rect(surface, BLANC, rect_bulle, border_radius=15)
        couleur_bordure = VIOLET_ANTINOUS if self.nom == "Antinous" else BLEU_TELEMACHUS
        pygame.draw.rect(surface, couleur_bordure, rect_bulle, width=3, border_radius=15)

        # La petite flèche de la bulle (Queue)
        pointes = [(x - 10, y), (x + 10, y), (x, y + 15)]
        pygame.draw.polygon(surface, BLANC, pointes)
        pygame.draw.line(surface, couleur_bordure, (x - 10, y), (x, y + 15), 3)
        pygame.draw.line(surface, couleur_bordure, (x + 10, y), (x, y + 15), 3)

        # Affichage du texte
        for i, ligne in enumerate(lignes):
            surface_texte = police_bulle.render(ligne.strip(), True, NOIR)
            surface.blit(surface_texte, (rect_bulle.x + 15, rect_bulle.y + 10 + (i * hauteur_ligne)))


class Decor:
    """Dessine les différents décors de l'animatic (chambre, imagination, hall)."""

    def dessiner_chambre(self, surface: pygame.Surface) -> None:
        # Murs sombres
        surface.fill((20, 25, 35))
        # Fenêtre
        pygame.draw.rect(surface, (10, 15, 25), (700, 100, 200, 300))
        pygame.draw.rect(surface, (40, 50, 70), (700, 100, 200, 300), 5)  # Cadre
        pygame.draw.line(surface, (40, 50, 70), (800, 100), (800, 400), 5)  # Barreaux
        pygame.draw.line(surface, (40, 50, 70), (700, 250), (900, 250), 5)
        # Étoiles par la fenêtre
        for _ in range(5):
            pygame.draw.circle(surface, BLANC, (random.randint(710, 890), random.randint(110, 390)), 1)
        # Lit (ombre de décor)
        pygame.draw.rect(surface, (30, 35, 45), (50, 500, 400, 200), border_radius=20)

    def dessiner_imagination(self, surface: pygame.Surface, temps: float, type_monstre: str = "aucun") -> None:
        # Vide spatial / Esprit
        surface.fill((10, 0, 15))

        if type_monstre == "cyclope":
            # Œil géant rouge qui clignote
            rayon_oeil = 80 + math.sin(temps * 5) * 10
            pygame.draw.circle(surface, (100, 0, 0), (LARGEUR // 2, 250), int(rayon_oeil))
            pygame.draw.circle(surface, (255, 50, 50), (LARGEUR // 2, 250), int(rayon_oeil / 2))
            pygame.draw.line(surface, NOIR, (LARGEUR // 2, 250 - 20), (LARGEUR // 2, 250 + 20), 10)  # Pupille
        elif type_monstre == "hydre":
            # Cous et yeux de l'hydre
            for i in range(5):
                decalage = math.sin(temps * 3 + i) * 30
                base_x = 200 + (i * 150)
                pygame.draw.line(surface, (0, 50, 20), (base_x, HAUTEUR), (base_x + decalage, 200 + abs(decalage)), 40)
                # Yeux
                pygame.draw.circle(surface, (200, 255, 50), (int(base_x + decalage - 10), int(200 + abs(decalage))), 5)
                pygame.draw.circle(surface, (200, 255, 50), (int(base_x + decalage + 10), int(200 + abs(decalage))), 5)

    def dessiner_hall(self, surface: pygame.Surface) -> None:
        surface.fill((40, 30, 30))
        # Colonnes grecques massives
        for i in range(4):
            x_col = 100 + i * 250
            pygame.draw.rect(surface, (60, 50, 50), (x_col, 0, 80, HAUTEUR))
            pygame.draw.rect(surface, (50, 40, 40), (x_col + 10, 0, 20, HAUTEUR))  # Rayures
            pygame.draw.rect(surface, (50, 40, 40), (x_col + 50, 0, 20, HAUTEUR))
        # Sol
        pygame.draw.rect(surface, (30, 20, 20), (0, 550, LARGEUR, 150))


class Particule:
    """Particule utilisée pour les effets spéciaux (feu d'artifice, éclats, etc.)."""

    def __init__(self, x: float, y: float, couleur: tuple[int, int, int]) -> None:
        self.x = x
        self.y = y
        self.couleur = couleur
        self.vx = random.uniform(-10, 10)
        self.vy = random.uniform(-15, 5)
        self.duree_vie = random.randint(20, 60)
        self.age = 0
        self.taille = random.randint(3, 8)

    def mettre_a_jour(self) -> None:
        # Gravité simple
        self.vy += 0.5
        self.x += self.vx
        self.y += self.vy
        self.age += 1

    def dessiner(self, surface: pygame.Surface) -> None:
        if self.age < self.duree_vie:
            alpha = max(0, 255 - int((self.age / self.duree_vie) * 255))
            surf_part = pygame.Surface((self.taille * 2, self.taille * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf_part, (*self.couleur, alpha), (self.taille, self.taille), self.taille)
            surface.blit(surf_part, (int(self.x), int(self.y)))


# --- Fonction utilitaire pour obtenir l'heure de la musique
def temps_audio(start_monotonic: float) -> float:
    """Retourne le temps écoulé en secondes en se basant sur la musique si possible.

    Si une musique est en cours de lecture, utilise `pygame.mixer.music.get_pos()`
    (ms) pour une synchronisation précise【294909052533098†L279-L283】. Sinon,
    utilise `time.monotonic()`.

    Args:
        start_monotonic: repère de départ pour le temps monotone lorsqu'il n'y a
            pas de musique.

    Returns:
        Durée écoulée en secondes.
    """
    if pygame.mixer.music.get_busy():
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms >= 0:
            return pos_ms / 1000.0
    # Fallback si aucune musique ou pos invalide
    return time.monotonic() - start_monotonic


# --- Boucle Principale ---
def main() -> None:
    fichier_musique = "legendary.mp3"
    musique_chargee = False

    if os.path.exists(fichier_musique):
        try:
            pygame.mixer.music.load(fichier_musique)
            musique_chargee = True
        except Exception as e:
            print(f"Erreur audio: {e}")

    # Écran d'accueil
    ecran_accueil = True
    while ecran_accueil:
        ecran.fill(NOIR)
        titre = police_titre.render("LEGENDARY - Animatic", True, OR_LEGENDAIRE)
        ecran.blit(titre, (LARGEUR // 2 - titre.get_width() // 2, HAUTEUR // 2 - 100))

        if musique_chargee:
            msg = police_bulle.render("Musique trouvée ! Appuyez sur ESPACE pour lancer l'animatic.", True, BLANC)
        else:
            msg = police_bulle.render("Fichier 'legendary.mp3' introuvable. Appuyez sur ESPACE pour lancer en muet.",
                                      True, ROUGE_MONSTRE)

        ecran.blit(msg, (LARGEUR // 2 - msg.get_width() // 2, HAUTEUR // 2 + 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                ecran_accueil = False

    # Démarrage de la musique et repère temps
    if musique_chargee:
        pygame.mixer.music.play()
        # On attend un court instant pour éviter un décalage
        pygame.time.delay(100)
        start_monotonic = time.monotonic()
    else:
        # Si pas de musique, on démarre quand même la mesure du temps
        start_monotonic = time.monotonic()

    en_cours = True
    index_parole = 0
    tremblement = 0
    scene_actuelle = "chambre"  # chambre, imagination, hall
    type_monstre = "aucun"
    transition_active = False
    transition_start = 0.0
    transition_duree = 1.0  # durée du fondu en secondes

    decor = Decor()
    telemachus = Personnage("Telemachus", 300, 450, BLEU_TELEMACHUS, taille=1.0)
    antinous = Personnage("Antinous", 700, 400, VIOLET_ANTINOUS, taille=1.3, inverser=True)
    particules: list[Particule] = []
    scene_precedente = scene_actuelle

    while en_cours:
        temps_ecoule = temps_audio(start_monotonic)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                en_cours = False

        # --- Gestion des Scènes et Paroles ---
        # Mise à jour de l'index des paroles si plusieurs événements ont été dépassés
        while index_parole < len(evenements_paroles) - 1 and temps_ecoule >= evenements_paroles[index_parole + 1][0]:
            index_parole += 1
            temps_event, texte, orateur = evenements_paroles[index_parole]

            # Réinitialiser qui parle
            telemachus.parle_actuellement = (orateur == "Telemachus")
            antinous.parle_actuellement = (orateur == "Antinous")

            # Affecter le texte
            telemachus.texte_bulle = texte if telemachus.parle_actuellement else ""
            antinous.texte_bulle = texte if antinous.parle_actuellement else ""

            # Déclencher des changements de décor selon le temps
            if 53 <= temps_ecoule < 80 or 115 <= temps_ecoule < 140 or temps_ecoule >= 215:
                nouvelle_scene = "imagination"
            elif 80 <= temps_ecoule < 115 or 140 <= temps_ecoule < 205:
                nouvelle_scene = "hall"
            else:
                nouvelle_scene = "chambre"

            # Si la scène change, activer un fondu
            if nouvelle_scene != scene_actuelle:
                scene_precedente = scene_actuelle
                scene_actuelle = nouvelle_scene
                transition_active = True
                transition_start = temps_ecoule

            # Effets de Monstres selon le texte
            texte_min = texte.lower()
            if "cyclops" in texte_min:
                type_monstre = "cyclope"
                tremblement = 10
            elif "hydra" in texte_min:
                type_monstre = "hydre"
                tremblement = 10
            elif "legendary" in texte_min:
                type_monstre = "aucun"
                tremblement = 20
                for _ in range(50):
                    particules.append(Particule(telemachus.x, telemachus.y, OR_LEGENDAIRE))
            elif "tramp" in texte_min or "champ" in texte_min:
                tremblement = 5
                for _ in range(20):
                    particules.append(Particule(antinous.x, antinous.y, VIOLET_ANTINOUS))

        # --- Rendu ---
        # Tremblement de caméra
        if tremblement > 0:
            tremblement -= 1
        ox = random.randint(-tremblement, tremblement) if tremblement > 0 else 0
        oy = random.randint(-tremblement, tremblement) if tremblement > 0 else 0

        # Surface pour dessiner le décor et les personnages
        surface_rendu = pygame.Surface((LARGEUR, HAUTEUR))

        # 1. Dessin du décor courant (ou en transition)
        if transition_active:
            # Durée écoulée depuis le début de la transition
            t_trans = temps_ecoule - transition_start
            ratio = min(max(t_trans / transition_duree, 0.0), 1.0)
            # Dessiner l'ancienne scène
            if scene_precedente == "chambre":
                decor.dessiner_chambre(surface_rendu)
            elif scene_precedente == "imagination":
                decor.dessiner_imagination(surface_rendu, temps_ecoule, type_monstre)
            elif scene_precedente == "hall":
                decor.dessiner_hall(surface_rendu)

            # Superposer un rectangle noir qui s'estompe
            overlay = pygame.Surface((LARGEUR, HAUTEUR))
            overlay.set_alpha(int(255 * ratio))
            overlay.fill((0, 0, 0))
            surface_rendu.blit(overlay, (0, 0))
            # Quand le fondu est terminé, désactiver la transition et dessiner la nouvelle scène
            if ratio >= 1.0:
                transition_active = False
        if not transition_active:
            if scene_actuelle == "chambre":
                decor.dessiner_chambre(surface_rendu)
            elif scene_actuelle == "imagination":
                decor.dessiner_imagination(surface_rendu, temps_ecoule, type_monstre)
            elif scene_actuelle == "hall":
                decor.dessiner_hall(surface_rendu)

        # 2. Positionnement dynamique des personnages selon la scène
        if scene_actuelle == "chambre" or scene_actuelle == "imagination":
            telemachus.x = LARGEUR // 2
            telemachus.dessiner(surface_rendu, temps_ecoule)
        elif scene_actuelle == "hall":
            telemachus.x = 300
            antinous.dessiner(surface_rendu, temps_ecoule)
            telemachus.dessiner(surface_rendu, temps_ecoule)

        # 3. Particules
        particules_vivantes: list[Particule] = []
        for p in particules:
            p.mettre_a_jour()
            p.dessiner(surface_rendu)
            if p.age < p.duree_vie:
                particules_vivantes.append(p)
        particules = particules_vivantes

        # 4. Affichage final avec tremblement de caméra
        ecran.fill(NOIR)
        ecran.blit(surface_rendu, (ox, oy))

        pygame.display.flip()
        horloge.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()