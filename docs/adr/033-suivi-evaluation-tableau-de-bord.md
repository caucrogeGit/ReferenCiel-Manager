# ADR-033 : Suivi et évaluation — tableau de bord multi-entrées et feuille de positionnement

**Statut :** Accepté
**Date :** 2026-07-21

## Contexte

L'ADR-032 a posé le modèle de la séance et la **règle d'évaluation** (les
observations s'accumulent, le professeur arbitre, pas d'auto-validation), et sa
phase C a **aligné le schéma** (`evaluation_activite` / `evaluation_critere`
enrichis et rattachés à la séance/l'élément). Il manque l'**expérience** de suivi
et d'évaluation : par où le professeur accède au travail des élèves et positionne
les critères.

Beaucoup existe déjà : les entités `classe`, `eleve`, `progression_sequence`
(statut, date, élève, séquence), `progression_seance` (statut, séance),
`bilan_eleve` ; un contrôleur **`/suivi`** (classes du prof → détail d'une classe
→ élèves et leur avancement) ; et le **graphe de suivi complet** en base.

## Décision

**1. Tableau de bord multi-entrées.** `/suivi` devient une page à **tuiles**,
chacune une **lentille** — un ordre de parcours du **même graphe** de suivi
(`classe ↔ eleve ↔ progression_sequence ↔ sequence ↔ progression_seance ↔
seance`) :

- **Par classe** : classe → élèves → historique de séquences → séances (en cours
  / à reprendre / à valider). *(Existe partiellement via `/suivi`.)*
- **Par séquence** : séquence → classes qui l'utilisent → élèves → séances.
- *(Extensible : par élève, par référentiel…)*

Les lentilles **convergent vers la même feuille**.

**2. Feuille de positionnement.** Le point d'arrivée : la page « travail d'un
élève sur une séance ». Le professeur y **positionne chaque critère observé**
(🔴 non acquis / 🟠 en cours / 🟩 acquis / 🟩 maîtrisé), avec l'**indicateur**
utilisé, la **production/preuve** et l'**aide** apportée (champs de la phase C).
Une observation = `evaluation_activite` + `evaluation_critere` (ADR-032).
L'accumulation et le **bilan** restent **arbitrés par le professeur** — pas de
validation automatique.

**3. Cycle de vie des progressions.** `progression_seance.statut` :
`non_commencee`, `en_cours`, `en_attente_validation`, `a_reprendre`, `validee`.
`progression_sequence.statut` : en cours / terminée. Les transitions
(`en_attente_validation → validee` / `a_reprendre`) sont des **actions du
professeur** depuis la feuille.

**4. Réutilisation.** On **étend `/suivi`** (contrôleur, modèle `suivi_eleves`)
plutôt que de repartir de zéro. Les entités progression/évaluation existantes
sont le socle.

## Conséquences

- `/suivi` : coquille **dashboard à tuiles** + lentilles (classe existe, séquence
  à ajouter) + drill-down jusqu'à la feuille.
- **Feuille** : nouvel écran de positionnement des critères d'un élève pour une
  séance (utilise les champs phase C : niveau, indicateur, production, aide).
- Le statut de `progression_seance` suit le cycle de vie ; les transitions sont
  des actions explicites du professeur.
- **Données** : le suivi n'a de sens qu'avec des élèves/classes/progressions ; un
  jeu de **démo** facilitera les tests.
- La feuille et le dashboard suivent la **charte** (comme les tunnels).

## Alternatives écartées

- **CRUD plat des `evaluation_*`** (statu quo) : pas de parcours métier,
  inutilisable au quotidien. Écarté.
- **Validation automatique par calcul** : contraire à ADR-032. Écarté.
- **Une seule entrée (par classe)** : la tuile « séquence » (voir toutes les
  classes d'une séquence) est un besoin exprimé. Écarté.

## Références

- `docs/adr/032-modele-seance-tunnel-cascade-evaluation.md` (modèle séance, règle
  d'évaluation, phase C schéma).
- `/suivi` existant ; entités `progression_sequence`/`progression_seance`,
  `evaluation_activite`/`evaluation_critere`, `bilan_eleve`.
