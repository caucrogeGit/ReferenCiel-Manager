# Checklist professeur : validation du palier 2

# Installer deux machines virtuelles avec VirtualBox

## Identification de l’élève

| Élément | Information |
|---|---|
| Nom | |
| Prénom | |
| Classe | |
| Poste utilisé | |
| Date de validation | |

## Objectif de la checklist

Cette checklist sert au professeur pour vérifier que l’élève a correctement terminé le palier 2.

Le palier est validé uniquement lorsque les deux machines virtuelles sont fonctionnelles, accessibles, mises à jour, équipées des additions invitées et sauvegardées par un instantané.

## 1. Validation du QCM

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| Le fichier `qcm-palier2.txt` existe | ☐ | ☐ | |
| Le fichier contient 20 réponses | ☐ | ☐ | |
| Le format est respecté, par exemple `1a`, `2b`, `3c` | ☐ | ☐ | |
| Le QCM est correct à 100 % | ☐ | ☐ | |
| L’élève a corrigé les erreurs éventuelles avant de commencer l’activité | ☐ | ☐ | |

Validation de cette partie :

| État | Décision |
|---|---|
| ☐ | QCM validé |
| ☐ | QCM à reprendre |

## 2. Vérification générale de VirtualBox

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| VirtualBox démarre correctement sur le poste Debian 13 | ☐ | ☐ | |
| Les deux machines virtuelles sont visibles dans VirtualBox | ☐ | ☐ | |
| Les noms des machines virtuelles sont clairs | ☐ | ☐ | |
| L’élève n’a pas créé de machines inutiles ou mal nommées | ☐ | ☐ | |

Noms attendus :

| Machine virtuelle | Nom attendu | Conforme |
|---|---|---|
| Windows 11 Pro | `VM-Windows-11-Pro` | ☐ |
| Zorin OS | `VM-Zorin` | ☐ |

## 3. Vérification de la machine virtuelle Windows 11 Pro

### 3.1 Configuration de la machine virtuelle

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| La machine virtuelle Windows existe | ☐ | ☐ | |
| Le nom est `VM-Windows-11-Pro` | ☐ | ☐ | |
| Le type est Microsoft Windows | ☐ | ☐ | |
| La version est Windows 11 64 bits | ☐ | ☐ | |
| L’image ISO Windows 11 a été utilisée | ☐ | ☐ | |
| L’édition installée est Windows 11 Pro | ☐ | ☐ | |
| La mémoire vive est conforme à la consigne | ☐ | ☐ | |
| Le nombre de processeurs est conforme à la consigne | ☐ | ☐ | |
| Le disque virtuel est conforme à la consigne | ☐ | ☐ | |
| Le stockage est en allocation dynamique | ☐ | ☐ | |
| Le mode réseau est laissé sur NAT pour l’installation | ☐ | ☐ | |
| EFI est activé si demandé | ☐ | ☐ | |
| TPM est activé si disponible | ☐ | ☐ | |
| Secure Boot est activé si disponible | ☐ | ☐ | |

### 3.2 Démarrage et session

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| La machine virtuelle démarre correctement | ☐ | ☐ | |
| Le bureau Windows s’affiche | ☐ | ☐ | |
| La session s’ouvre avec le compte `tne` | ☐ | ☐ | |
| Le mot de passe commun fonctionne | ☐ | ☐ | |
| Aucun compte personnel n’a été utilisé | ☐ | ☐ | |
| Le compte utilisé est un compte local | ☐ | ☐ | |

### 3.3 Mise à jour et arrêt

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| Windows Update a été lancé | ☐ | ☐ | |
| Les mises à jour disponibles ont été installées | ☐ | ☐ | |
| La machine a été redémarrée si nécessaire | ☐ | ☐ | |
| Une nouvelle recherche de mises à jour a été faite après redémarrage | ☐ | ☐ | |
| Windows s’arrête proprement | ☐ | ☐ | |
| L’élève ne ferme pas brutalement la fenêtre de la machine virtuelle | ☐ | ☐ | |

### 3.4 Additions invitées Windows

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| Les additions invitées ont été insérées depuis le menu VirtualBox | ☐ | ☐ | |
| `VBoxWindowsAdditions.exe` a été lancé | ☐ | ☐ | |
| Windows a été redémarré après installation | ☐ | ☐ | |
| L’affichage s’adapte correctement à la fenêtre | ☐ | ☐ | |
| La souris est fluide dans la machine virtuelle | ☐ | ☐ | |

### 3.5 Instantané Windows

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| Windows est dans un état propre avant l’instantané | ☐ | ☐ | |
| La machine virtuelle est arrêtée proprement avant l’instantané | ☐ | ☐ | |
| L’instantané existe | ☐ | ☐ | |
| Le nom de l’instantané est `Installation propre` | ☐ | ☐ | |

Validation Windows 11 Pro :

| État | Décision |
|---|---|
| ☐ | Windows 11 Pro validé |
| ☐ | Windows 11 Pro à reprendre |

## 4. Vérification de la machine virtuelle Zorin OS

### 4.1 Configuration de la machine virtuelle

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| La machine virtuelle Zorin OS existe | ☐ | ☐ | |
| Le nom est `VM-Zorin` | ☐ | ☐ | |
| Le type est Linux | ☐ | ☐ | |
| La version est Ubuntu 64 bits | ☐ | ☐ | |
| L’image ISO Zorin OS a été utilisée | ☐ | ☐ | |
| La mémoire vive est conforme à la consigne | ☐ | ☐ | |
| Le nombre de processeurs est conforme à la consigne | ☐ | ☐ | |
| Le disque virtuel est conforme à la consigne | ☐ | ☐ | |
| Le stockage est en allocation dynamique | ☐ | ☐ | |
| Le mode réseau est laissé sur NAT pour l’installation | ☐ | ☐ | |
| La mémoire vidéo est conforme à la consigne | ☐ | ☐ | |

### 4.2 Installation et session

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| Zorin OS démarre correctement | ☐ | ☐ | |
| Le bureau Zorin OS s’affiche | ☐ | ☐ | |
| Le compte utilisateur est `tne` | ☐ | ☐ | |
| Le mot de passe commun fonctionne | ☐ | ☐ | |
| Le nom de l’ordinateur est `zorin-tne` | ☐ | ☐ | |
| Aucun identifiant personnel n’a été utilisé | ☐ | ☐ | |
| Le système demande le mot de passe à l’ouverture de session | ☐ | ☐ | |

### 4.3 Mise à jour et arrêt

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| La mise à jour a été lancée | ☐ | ☐ | |
| La commande `sudo apt update` a été exécutée | ☐ | ☐ | |
| La commande `sudo apt upgrade` a été exécutée | ☐ | ☐ | |
| Le système a été redémarré si nécessaire | ☐ | ☐ | |
| Zorin OS s’arrête proprement | ☐ | ☐ | |
| L’élève ne ferme pas brutalement la fenêtre de la machine virtuelle | ☐ | ☐ | |

### 4.4 Additions invitées Zorin OS

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| Les paquets nécessaires ont été installés | ☐ | ☐ | |
| L’image CD des additions invitées a été insérée | ☐ | ☐ | |
| Le CD des additions invitées a été monté | ☐ | ☐ | |
| `VBoxLinuxAdditions.run` a été exécuté | ☐ | ☐ | |
| Zorin OS a été redémarré après installation | ☐ | ☐ | |
| L’affichage s’adapte correctement à la fenêtre | ☐ | ☐ | |
| La souris est fluide dans la machine virtuelle | ☐ | ☐ | |

### 4.5 Instantané Zorin OS

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| Zorin OS est dans un état propre avant l’instantané | ☐ | ☐ | |
| La machine virtuelle est arrêtée proprement avant l’instantané | ☐ | ☐ | |
| L’instantané existe | ☐ | ☐ | |
| Le nom de l’instantané est `Installation propre` | ☐ | ☐ | |

Validation Zorin OS :

| État | Décision |
|---|---|
| ☐ | Zorin OS validé |
| ☐ | Zorin OS à reprendre |

## 5. Vérification de l’autonomie de l’élève

| Point à vérifier | Oui | Non | Observation |
|---|---|---|---|
| L’élève utilise le dossier technique pour chercher les informations | ☐ | ☐ | |
| L’élève ne demande pas directement la solution sans recherche préalable | ☐ | ☐ | |
| L’élève sait indiquer le chapitre consulté dans le dossier technique | ☐ | ☐ | |
| L’élève sait expliquer ce qu’il a fait | ☐ | ☐ | |
| L’élève sait expliquer ce qu’il a observé | ☐ | ☐ | |
| L’élève sait expliquer ce qui bloque | ☐ | ☐ | |

Formulation attendue en cas de demande d’aide :

| Point attendu | Oui | Non | Observation |
|---|---|---|---|
| L’élève indique l’étape concernée | ☐ | ☐ | |
| L’élève indique la machine virtuelle concernée | ☐ | ☐ | |
| L’élève indique ce qu’il a déjà essayé | ☐ | ☐ | |
| L’élève indique ce qu’il observe | ☐ | ☐ | |
| L’élève indique la partie du dossier consultée | ☐ | ☐ | |
| L’élève formule une demande précise | ☐ | ☐ | |

## 6. Validation finale du palier 2

| Élément final à valider | Oui | Non | Observation |
|---|---|---|---|
| QCM validé à 100 % | ☐ | ☐ | |
| VM Windows 11 Pro installée | ☐ | ☐ | |
| VM Windows 11 Pro accessible avec le compte demandé | ☐ | ☐ | |
| VM Windows 11 Pro à jour | ☐ | ☐ | |
| Additions invitées installées sur Windows 11 Pro | ☐ | ☐ | |
| Instantané Windows 11 Pro créé | ☐ | ☐ | |
| VM Zorin OS installée | ☐ | ☐ | |
| VM Zorin OS accessible avec le compte demandé | ☐ | ☐ | |
| VM Zorin OS à jour | ☐ | ☐ | |
| Additions invitées installées sur Zorin OS | ☐ | ☐ | |
| Instantané Zorin OS créé | ☐ | ☐ | |
| Les deux machines virtuelles sont prêtes pour le palier 3 | ☐ | ☐ | |

Décision finale :

| État | Décision |
|---|---|
| ☐ | Palier 2 validé |
| ☐ | Palier 2 à reprendre |
| ☐ | Validation partielle, correction demandée |

Commentaire professeur :

....................................................................................................

....................................................................................................

....................................................................................................
