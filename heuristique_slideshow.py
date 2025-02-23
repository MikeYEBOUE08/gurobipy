import argparse
from typing import List, Set, Dict, Tuple

class Photo:
    def __init__(self, id: int, is_horizontal: bool, tags: Set[str]):
        self.id = id
        self.is_horizontal = is_horizontal
        self.tags = tags

def read_input_file(input_file: str) -> List[Photo]:
    """
    Lire le fichier d'entrée et retourner une liste de photos.
    """
    photos = []
    with open(input_file, "r") as file:
        N = int(file.readline().strip())
        for i in range(N):
            data = file.readline().strip().split()
            orientation = data[0]
            tags = set(data[2:])
            photos.append(Photo(i, orientation == "H", tags))
    return photos

def read_solution_file(solution_file: str) -> List[List[int]]:
    """
    Lire le fichier de solution et retourner la liste des slides.
    """
    with open(solution_file, "r") as file:
        slides = []
        N = int(file.readline().strip())
        for _ in range(N):
            slide = list(map(int, file.readline().strip().split()))
            slides.append(slide)
    return slides

def verify_solution(photos: List[Photo], slides: List[List[int]]) -> Tuple[bool, str]:
    """
    Vérifier si la solution est réalisable.
    """
    used_photos = set()
    
    for slide_idx, slide in enumerate(slides):
        # Vérifier le nombre de photos par slide
        if len(slide) not in [1, 2]:
            return False, f"Slide {slide_idx} contient un nombre invalide de photos: {len(slide)}"
        
        # Vérifier si les IDs sont valides
        for photo_id in slide:
            if photo_id >= len(photos) or photo_id < 0:
                return False, f"ID de photo invalide dans le slide {slide_idx}: {photo_id}"
            
        # Vérifier l'utilisation unique des photos
        for photo_id in slide:
            if photo_id in used_photos:
                return False, f"Photo {photo_id} utilisée plusieurs fois"
            used_photos.add(photo_id)
        
        # Vérifier l'orientation des photos
        if len(slide) == 1:
            if not photos[slide[0]].is_horizontal:
                return False, f"Photo verticale {slide[0]} utilisée seule dans le slide {slide_idx}"
        else:  # len(slide) == 2
            if photos[slide[0]].is_horizontal or photos[slide[1]].is_horizontal:
                return False, f"Photos horizontales dans une paire au slide {slide_idx}"
    
    return True, "Solution réalisable"

def compute_slide_tags(photos: List[Photo], slide: List[int]) -> Set[str]:
    """
    Calculer l'ensemble des tags pour un slide.
    """
    tags = set()
    for photo_id in slide:
        tags.update(photos[photo_id].tags)
    return tags

def compute_interest_factor(tags1: Set[str], tags2: Set[str]) -> int:
    """
    Calculer le facteur d'intérêt entre deux ensembles de tags.
    """
    common_tags = len(tags1.intersection(tags2))
    tags_in_1_not_2 = len(tags1 - tags2)
    tags_in_2_not_1 = len(tags2 - tags1)
    return min(common_tags, tags_in_1_not_2, tags_in_2_not_1)

def compute_total_score(photos: List[Photo], slides: List[List[int]]) -> int:
    """
    Calculer le score total de la solution.
    """
    if len(slides) <= 1:
        return 0
    
    total_score = 0
    for i in range(len(slides) - 1):
        tags1 = compute_slide_tags(photos, slides[i])
        tags2 = compute_slide_tags(photos, slides[i + 1])
        score = compute_interest_factor(tags1, tags2)
        total_score += score
    return total_score

def combine_vertical_photos(photos_vertical: List[Photo]) -> List[Dict]:
    """
    Combiner les photos verticales en paires optimales.
    """
    slides = []
    while len(photos_vertical) > 1:
        photo1 = photos_vertical.pop(0)
        best_score = -1
        best_idx = -1
        
        for i, photo2 in enumerate(photos_vertical):
            combined_tags = photo1.tags.union(photo2.tags)
            score = len(combined_tags)
            if score > best_score:
                best_score = score
                best_idx = i
        
        photo2 = photos_vertical.pop(best_idx)
        slides.append({
            "ids": [photo1.id, photo2.id],
            "tags": photo1.tags.union(photo2.tags)
        })
    
    return slides

def optimize_slide_order(slides: List[Dict]) -> List[Dict]:
    """
    Optimiser l'ordre des slides pour maximiser le score.
    """
    if not slides:
        return slides
    
    ordered_slides = [slides.pop(0)]
    
    while slides:
        best_score = -1
        best_idx = -1
        
        for i, slide in enumerate(slides):
            score = compute_interest_factor(ordered_slides[-1]["tags"], slide["tags"])
            if score > best_score:
                best_score = score
                best_idx = i
        
        ordered_slides.append(slides.pop(best_idx))
    
    return ordered_slides

def write_output_file(slides: List[Dict], output_file: str = "slideshow.sol"):
    """
    Écrire la solution dans le fichier de sortie.
    """
    with open(output_file, "w") as file:
        file.write(f"{len(slides)}\n")
        for slide in slides:
            file.write(" ".join(map(str, slide["ids"])) + "\n")

def main():
    parser = argparse.ArgumentParser(description='Génère et vérifie un diaporama optimisé')
    parser.add_argument('input_file', help='Chemin vers le fichier d\'entrée')
    args = parser.parse_args()

    # Lecture des photos
    print(f"Lecture du fichier d'entrée: {args.input_file}")
    photos = read_input_file(args.input_file)
    
    # Séparation des photos horizontales et verticales
    photos_horizontal = [p for p in photos if p.is_horizontal]
    photos_vertical = [p for p in photos if not p.is_horizontal]
    
    print(f"Nombre de photos horizontales: {len(photos_horizontal)}")
    print(f"Nombre de photos verticales: {len(photos_vertical)}")
    
    # Création des slides
    slides = []
    # Ajout des photos horizontales
    slides.extend([{"ids": [photo.id], "tags": photo.tags} for photo in photos_horizontal])
    # Ajout des paires verticales
    slides.extend(combine_vertical_photos(photos_vertical))
    
    print(f"Nombre total de slides créés: {len(slides)}")
    
    # Optimisation de l'ordre
    print("Optimisation de l'ordre des slides...")
    slides = optimize_slide_order(slides)
    
    # Écriture de la solution
    write_output_file(slides)
    print("Solution écrite dans slideshow.sol")
    
    # Vérification de la solution
    solution_slides = read_solution_file("slideshow.sol")
    is_feasible, message = verify_solution(photos, solution_slides)
    
    print("\nVérification de la solution:")
    print(f"Statut: {message}")
    
    if is_feasible:
        score = compute_total_score(photos, solution_slides)
        print(f"Score de la solution: {score}")
        
        # Calcul des statistiques
        nb_transitions = len(solution_slides) - 1
        if nb_transitions > 0:
            print(f"Score moyen par transition: {score/nb_transitions:.2f}")
        print(f"Nombre de slides dans la solution: {len(solution_slides)}")

if __name__ == "__main__":
    main()