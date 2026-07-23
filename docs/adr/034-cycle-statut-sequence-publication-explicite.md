# ADR-034 : Cycle de statut de la séquence, entièrement dérivé des données

## Statut

Accepté (révisé le jour même : la publication par case à cocher, envisagée en
première version, est remplacée par un cycle entièrement dérivé).

## Date

2026-07-22

## Contexte

Le scénario a un statut dérivé des données (ADR-019) : « brouillon » puis
« finalisé » dès qu'il est complet, jamais saisi à la main.
La séquence, elle, n'avait aucun recalcul : son statut restait « brouillon »
(ou « publié » posé par les données de démonstration), sans règle.
Une première version de cette décision introduisait une case « Publiée » sur la
carte ; à l'usage, « finalisé » et « publié » sont bien deux informations
distinctes, et une exigence de séance pour finaliser aurait créé un cercle
impossible avec la règle « les séances se lient aux séquences publiées ».
Le porteur a tranché pour un cycle où chaque état découle d'un fait observable.

## Décision

1. La séquence suit le cycle « brouillon », « finalise », « publie »,
   « attribue », **entièrement dérivé des données**, sans commande manuelle :
   - **brouillon** : tunnel incomplet ;
   - **finalise** : tunnel complet (titre et niveau de classe renseignés, et au
     moins une connaissance retenue quand un référentiel est rattaché ; hors
     référentiel, titre et niveau suffisent) ;
   - **publie** : complète ET au moins une séance liée ;
   - **attribue** : au moins une progression élève existe ; cet état prime sur
     tout (la séquence est en usage, figée par instantané, ADR-026).
2. La règle pure vit dans `mvc/services/sequence_tunnel.py`
   (`statut_sequence_cible`) ; le recalcul persisté dans
   `mvc/models/sequence_model.py` (`recalculer_statut`), appelé à chaque
   écriture qui peut changer l'état : identité du tunnel, savoirs, référentiel,
   création/modification/suppression de séance, création/modification/
   suppression de progression.
3. Une séance se lie dès que la séquence est **finalisée** ; la première séance
   liée fait passer la séquence en « publie ».
   Le sélecteur de création ne propose que ces séquences et la garde serveur
   refuse toute autre valeur.
4. Badges : « Publié » garde le style de « Finalisé » (l'étape de complétude
   reste lisible) ; « Attribué » passe au vert, comme « Utilisé » côté scénario.
5. Le verrou de référentiel de la paire (ADR-029) couvre « finalise »,
   « publie » et « attribue ».

## Conséquences

- Chaque état répond à une question simple : complète ? a des séances ? a des
  élèves ? Aucun état ne peut mentir ni être oublié.
- Le flux de travail devient : compléter le tunnel, puis construire les
  séances, puis attribuer aux élèves ; l'interface guide sans bouton de plus.
- Le statut reste stocké en base et tenu à jour à l'écriture, donc jamais
  falsifiable ni recalculé à la lecture.
- Les séquences existantes gagnent leur statut recalculé à leur prochaine
  écriture (tunnel, séance ou progression), pas rétroactivement.

## Alternatives écartées

- Case « Publiée » manuelle sur la carte : rejetée après essai, elle écrasait
  visuellement « finalisé » et ajoutait une décision là où un fait observable
  (une séance liée) suffit.
- Exiger une séance pour « finalise » : rejeté, cercle impossible tant que les
  séances ne se lient qu'aux séquences déjà publiées.
- Un champ « publié » booléen séparé du statut : rejeté, deux sources de vérité
  pour un même cycle de vie.

## Complément (2026-07-24) — l'organisation des séances est un choix conscient

Sur retour du porteur : la finalisation exige, en plus du titre et du niveau,
que l'**organisation des séances** (ordre libre, ordre imposé, glissante) soit
**explicitement choisie**.
Les deux drapeaux du contrat (`activite_glissante`, `ordre_impose`) deviennent
nullables : NULL/NULL signifie « à préciser » (état de création, aucun mode
présélectionné) ; un défaut « ordre libre » silencieux pouvait installer une
erreur pédagogique.
La complétude de l'étape Titre et `statut_sequence_cible` intègrent ce choix ;
les séquences existantes repassent « à préciser » (leur « libre » n'était qu'un
défaut, jamais un choix).
