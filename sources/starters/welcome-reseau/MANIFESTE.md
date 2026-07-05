# Manifeste — Starter « Welcome Réseau » (2TNE CIEL)

Source **pédagogique interne** (instructions §4) : un parcours créé et éprouvé en
classe par le professeur. Déposée pour numérisation et traitement automatisé
ultérieur par RéférenCiel Manager.

> **Statut source** : matériau d'origine, conservé fidèlement. Le nettoyage (retrait
> du *chrome* de site, extraction structurée) se fait à la **canonicalisation**
> (JSON canonique, tickets 02/03), pas ici — un source reste fidèle.

## Nature et rôle

- **Type** : *Starter Welcome* — un parcours pédagogique réutilisable (≠ référentiel
  niveau-classe). C'est le **2ᵉ exemple canonique** du projet, complémentaire du
  référentiel CIEL 2TNE : ensemble ils **façonnent le contrat du JSON canonique**
  (ticket 02).
- **Thème** : semaine réseau & virtualisation, classe 2TNE CIEL.

## Modèle pédagogique (la « forme »)

Parcours en **4 paliers ordonnés**, chaque palier en 3 temps :

```text
Dossier technique  →  QCM (validé à 100 % obligatoire)  →  Activité pratique
```

Règles structurantes : activité glissante (rythme propre) ; portes de validation
(QCM 100 % avant activité, validation professeur avant palier suivant, ordre
imposé) ; démarche technicien (lire → préparer → réaliser → tester → observer →
corriger → conclure) ; protocole d'aide structuré ; checklist à double colonne
élève/professeur + décision finale.

| Palier | Thème | Production attendue |
|--:|---|---|
| 1 | Câble Ethernet droit T568B | Un câble droit conforme |
| 2 | Machines virtuelles (VirtualBox) | 2 VM (Win 11 / Linux) + instantané |
| 3 | Modes réseau NAT / accès par pont | Tableau de tests des deux modes |
| 4 | Réseau interne + diagnostic | Réseau interne fonctionnel + diagnostic |

## Structure des fichiers

```text
welcome-reseau/
  index.md                       # parcours (présentation, organisation, paliers)
  palier-N/
    index.md                     # palier (documents + ordre de travail)
    dossier-technique.md         # connaissances du palier
    eleve/      qcm · activite · checklist (validation)
    professeur/ qcm-corrige
    images/     schémas (PNG)
```

## Correspondance avec les objets métier (chaîne « définition »)

`Parcours` → `Palier` → { `DocumentTechnique` ; `QCM` → `QuestionQCM` → `ChoixQCM`
(+ **bonne réponse** via le corrigé) ; `Activité` ; `Checklist` → `ItemChecklist`
(colonnes élève/professeur = préfiguration de `Progression` / `ÉvaluationCritère`) }
+ `Ressource` (élève / professeur) + `Image`. Le starter encode aussi des **règles
de progression** (gate QCM 100 %, ordre, validation professeur).

## État de numérisation

| Contenu | Palier 1 | Palier 2 | Palier 3 | Palier 4 |
|---|:--:|:--:|:--:|:--:|
| Dossier technique (.md natif) | ✅ | ✅ | ✅ | ✅ |
| QCM | 🆕 transcrit | 🆕 transcrit | ✅ .md | ✅ .md |
| Activité | 🆕 transcrit | 🆕 transcrit | ✅ .md | ✅ .md |
| Checklist validation | ✍️ générée | 🆕 transcrit | ✅ .md | ✅ .md |
| Corrigé QCM (professeur) | 🆕 transcrit | ✅ dégroupé | ✅ .md | ✅ .md |

- ✅ déjà en markdown · 🆕 transcrit du PDF (paliers 1-2) · ✍️ **contenu généré**
  (≠ source, à valider par le professeur) · les PDF originaux sont **conservés** à
  côté des `.md` (traçabilité).

### Anomalies de source à signaler (retour au professeur)

Constatées à la transcription :

- **Corrigés groupés → dégroupés** : le PDF `qcm-palier-1-corrige.pdf` regroupe les
  corrigés des paliers 1 ET 2 (40 questions). Les markdown ont été **dégroupés** :
  `palier-1/professeur/qcm-palier-1-corrige.md` (P1) et
  `palier-2/professeur/qcm-palier-2-corrige.md` (P2). Le PDF original reste groupé
  (conservé fidèlement côté palier 1).
- **Palier 1** : checklist de validation **absente de la source d'origine** →
  **générée** (`checklist-palier-1-validation.md`, colonnes Élève/Professeur,
  marquée « à valider ») sur le modèle des paliers 2-3-4 et à partir de l'activité
  du palier 1. Contenu produit, pas source : à relire par le professeur.
- **Format de checklist divergent** : le palier 2 utilise des colonnes
  « Oui / Non / Observation », le palier 3 des colonnes « Élève / Professeur ». À
  uniformiser à la canonicalisation.
- **Nommage** : le QCM du palier 2 renvoie à un fichier réponse `qcm-palier2.txt`
  (sans tiret) alors que les documents sont nommés `qcm-palier-2` (avec tiret).

## Inventaire des images (33 PNG)

**Palier 1** (câble/RJ45) : `cable-droit-t568b`, `connecteur-rj45-vue-face`,
`constitution-cable-ethernet`, `erreurs-cablage-rj45`, `norme-t568b`,
`reseau-local`, `reseau-physique-logique`, `testeur-rj45`.

**Palier 2** (virtualisation) : `erreurs-virtualbox`, `image-iso-installation`,
`instantane-machine-virtuelle`, `machine-hote-machine-invitee`,
`parametres-vm-windows-zorin`, `principe-virtualisation`,
`procedure-installation-vm`, `ressources-machine-virtuelle`.

**Palier 3** (modes réseau) : `01-hote-et-machines-virtuelles`,
`02-cartes-reseau-reelle-et-virtuelles`, `03-tests-mode-nat-et-pont`,
`04-adresse-ip-masque-passerelle`, `05-dhcp-adresse-ip-automatique`,
`06-commandes-reseau-linux`, `07-commandes-reseau-windows`,
`09-comprendre-mode-nat`, `10-tester-mode-nat-virtualbox`,
`11-comprendre-mod-pont`, `13-comparaison-nat-pont`.

**Palier 4** (réseau interne) : `01-machines-utilisees`, `03-role-reseau-interne`,
`05-adresse-ip-meme-reseau-logique`, `10-pare-feu-windows-et-ping`,
`14-convertir-octet-binaire`, `15-calculer-reseau-adresse-ip`.

> Le nom de fichier tient lieu de légende. Un alt-text/OCR enrichi (référencé-par
> quel dossier technique) est un raffinement possible à la canonicalisation.

## Chrome de site à retirer à la canonicalisation

Vestiges du site Forge où ce support vivait temporairement : bandeaux
`<!-- PAGE TEMPORAIRE … -->`, admonitions `!!! warning "Page temporaire…"`, liens
de navigation (`[Accueil](…)`, boutons « Retour »). Non pertinents comme source ;
à écarter lors de l'extraction du JSON canonique.
