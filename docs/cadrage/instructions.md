# Instructions projet RéférenCiel Manager

## 1. Rôle de ce fichier

Ce fichier fixe les instructions prioritaires du projet RéférenCiel Manager.

Il doit être lu et appliqué avant les autres documents du projet, sauf demande explicite contraire de l'utilisateur.

Le projet doit être compris comme autonome.
Ne pas supposer que les conversations précédentes existent encore.
Les décisions importantes doivent être reprises depuis ce fichier et depuis les fichiers de référence présents dans le dossier projet.

## 2. Définition du projet

RéférenCiel Manager est une application métier pédagogique persistée, construite avec le framework Forge.

Elle permet de créer, organiser, affecter, suivre et évaluer des parcours pédagogiques pour différentes classes de niveau, à partir de scénarios pédagogiques, de référentiels de formation, de JSON canoniques métier et de starters Welcome réutilisables.

L'application doit gérer :

- les référentiels de formation ;
- les vues de référentiel par niveau de classe ;
- les pôles d'activités ;
- les activités professionnelles ;
- les tâches associées ;
- les compétences ;
- les critères observables ;
- les résultats attendus ;
- les indicateurs de réussite pédagogiques ;
- les scénarios pédagogiques ;
- les starters Welcome ;
- les séquences pédagogiques ;
- les séances pédagogiques ;
- les dossiers techniques ;
- les QCM de compréhension ;
- les checklists ;
- les ressources élèves et professeur ;
- les affectations à des classes ou à des élèves ;
- la progression individuelle des élèves ;
- le suivi professeur par classe, niveau, séquence, séance et compétence ;
- les évaluations par critères ;
- les bilans exploitables par le professeur.

RéférenCiel Manager n'est pas seulement un outil de création de parcours. C'est une application de conception, de diffusion, de suivi et d'évaluation pédagogique.

## 3. Documents de référence

Le fichier prioritaire est :

```text
instructions.md
```

Le fichier de cadrage métier principal est :

```text
cadre-projet-referenciel-manager.md
```

Les documents de référence attendus dans les sources du projet sont :

```text
instructions.md
cadre-projet-referenciel-manager.md
roadmap-referenciel-manager-exhaustive.md
referenciel-bac-pro-ciel.pdf
trace-creation-json-canonique-cpro-2tne.md
```

Les documents issus de l'ancienne trajectoire V0 fichier peuvent rester en archive, mais ils ne doivent pas réactiver une construction fondée sur `path.yml`, `palier.yml`, `qcm.yml` ou `checklist.yml` comme source principale.

En cas de contradiction entre un ancien document et le cadre actuel, le cadre actuel l'emporte.

## 4. Sources du projet

Les données du projet peuvent venir de plusieurs sources.

Sources institutionnelles ou officielles :

- référentiel officiel Bac Pro CIEL ;
- référentiels de formation publiés par l'Éducation nationale ;
- documents académiques ;
- documents d'accompagnement pédagogique.

Sources exportées ou reconstruites :

- fichiers `.scpro` exportés depuis CPRO ;
- fichiers `.odt` obtenus par export ou conversion depuis CPRO ;
- exports textuels ou structurés issus de CPRO ;
- JSON canoniques produits à partir de ces exports.

Sources pédagogiques internes :

- starters Welcome, notamment Welcome Réseau ;
- dossiers techniques existants ;
- QCM existants ;
- checklists existantes ;
- activités existantes ;
- ressources créées par le professeur ;
- contenus importés depuis une autre instance RéférenCiel Manager.

Règle de provenance :

```text
Toute donnée reprise, extraite, reconstruite ou adaptée depuis une source doit conserver une trace de provenance.
```

Le document `trace-creation-json-canonique-cpro-2tne.md` sert à documenter la chaîne :

```text
fichier .scpro CPRO
-> fichier .odt exporté ou converti
-> référentiel officiel Bac Pro CIEL
-> extraction ciblée pour un niveau de classe
-> JSON canonique métier
-> dictionnaire de données
-> import ou construction applicative
```

## 5. JSON canonique métier

Les JSON canoniques ont un statut central dans le projet.

Un JSON canonique n'est pas une simple sauvegarde technique. C'est une représentation structurée, maîtrisée et stable des informations utiles au projet.

Il peut servir à :

- analyser une source ;
- normaliser une exportation CPRO ;
- formaliser une extraction du référentiel officiel ;
- représenter un starter Welcome ;
- construire des scénarios ;
- documenter les objets métier ;
- générer ou préremplir le dictionnaire de données ;
- valider la cohérence d'un modèle ;
- importer des objets en base ;
- servir de fixture de test ou de seed contrôlé.

Formule à retenir :

```text
JSON canonique = référence structurée de construction ou d'import
Dictionnaire de données = documentation métier enrichie et canonique
Base de données = vérité applicative en fonctionnement
```

## 6. JSON canonique de référentiel niveau-classe

Le JSON issu du traitement d'un fichier `.scpro` CPRO et d'un fichier `.odt` exporté depuis CPRO ne doit pas être considéré comme un simple JSON de scénario.

Il doit être considéré comme un :

```text
JSON canonique de référentiel niveau-classe
```

Exemple :

```text
JSON canonique CIEL 2TNE
```

Ce JSON formalise une extraction spécifique du référentiel Bac Pro CIEL pour un niveau de classe donné.

Il peut contenir :

- la formation ;
- le niveau de classe ;
- les pôles d'activités ;
- les activités professionnelles ;
- les tâches associées ;
- les conditions d'exercice utiles ;
- les résultats attendus ;
- les compétences associées ;
- les critères d'évaluation ;
- les relations entre activités et compétences ;
- les indicateurs de réussite exploitables pédagogiquement ;
- la provenance des données.

Attention au vocabulaire :

```text
Dans le référentiel officiel, on parle de pôles d'activités, pas de rôles.
```

Le terme `rôles` doit être réservé aux rôles applicatifs comme `eleve`, `professeur` ou `administrateur`, sauf cas métier explicitement défini.

## 7. Résultats attendus, critères et indicateurs

Il faut distinguer trois notions.

### Résultats attendus

Les résultats attendus sont liés aux activités professionnelles.

Exemple : pour une activité comme E1, E2, R1 ou R2, le référentiel décrit des tâches, des conditions d'exercice, une autonomie et des résultats attendus.

### Critères d'évaluation

Les critères d'évaluation sont liés aux compétences.

Exemple : une compétence comme C03, C07, C09 ou C11 possède des critères permettant d'évaluer la compétence.

### Indicateurs de réussite pédagogiques

Les indicateurs de réussite sont des formulations exploitables dans RéférenCiel Manager.

Ils peuvent être :

- repris directement d'un résultat attendu ;
- repris directement d'un critère d'évaluation ;
- adaptés pour un niveau de classe ;
- reformulés par le professeur pour un scénario, un starter, un parcours, une activité ou une checklist.

Règle :

```text
resultats_attendus = liés aux activités professionnelles
criteres_evaluation = liés aux compétences
indicateurs_reussite = formulation pédagogique exploitable dans RéférenCiel Manager
```

## 8. Chaîne de transformation des sources

La chaîne de transformation cible est :

```text
source originelle
-> extraction
-> JSON canonique métier
-> schéma JSON
-> dictionnaire de données généré ou prérempli
-> dictionnaire de données enrichi
-> modèle relationnel
-> contrat d'entité Forge
-> migration SQL
-> import en base
-> services métier
-> interfaces
-> tests
```

La source originelle n'impose jamais directement le modèle applicatif.

Le JSON canonique structure l'information extraite.

Le dictionnaire de données documente le modèle métier et l'enrichit avec les règles applicatives.

La base de données contient l'état réel de l'application en fonctionnement.

## 9. Dictionnaire de données

Le dictionnaire de données est la documentation métier enrichie du modèle.

Il peut être généré ou prérempli à partir des JSON canoniques, mais il doit aller plus loin que le JSON.

Il doit préciser :

- le sens métier des objets ;
- le sens métier des champs ;
- les relations ;
- les cardinalités ;
- les règles de validation ;
- les règles de visibilité ;
- les règles de modification ;
- les règles de publication ;
- les règles de versionnement ;
- les droits d'accès ;
- les impacts sur l'exécution élève ;
- les impacts sur le suivi professeur.

Le dictionnaire de données sert ensuite à déduire :

- le modèle relationnel ;
- le diagramme de classes ;
- les contrats d'entités Forge ;
- les migrations SQL ;
- les repositories ;
- les services métier ;
- les tests.

## 10. Base de données

La base de données est la source de vérité de l'application en fonctionnement.

Elle contient les objets réellement utilisés, modifiés, publiés, affectés, évalués ou suivis.

Une fois un objet importé, modifié, publié ou affecté, l'application ne doit pas dépendre d'un fichier externe pour connaître son état réel.

Tous les objets métier utilisés par l'application doivent posséder une identité en base quand ils deviennent exploitables dans l'application.

## 11. Positionnement

RéférenCiel Manager n'est pas :

- un gestionnaire de PDF ;
- un visualiseur de Markdown ;
- une V0 fichier ;
- un simple dossier de fichiers YAML ;
- un clone de CPRO ;
- un ENT ;
- un LMS généraliste ;
- une simple interface CRUD sans métier.

RéférenCiel Manager est une application métier persistée centrée sur :

- les JSON canoniques métier ;
- les référentiels de formation ;
- les vues de référentiel par niveau de classe ;
- les scénarios pédagogiques ;
- les starters Welcome ;
- les séquences pédagogiques ;
- le suivi professeur ;
- l'évaluation par critères ;
- la progression contrôlée ;
- la traçabilité des sources pédagogiques.

Différence avec CPRO :

- CPRO suit et structure l'évaluation par compétences ;
- RéférenCiel Manager structure le parcours pédagogique qui conduit à cette évaluation ;
- RéférenCiel Manager peut s'inspirer de la logique CPRO, mais ne doit pas dépendre techniquement de CPRO.

## 12. Chaîne pédagogique centrale

La chaîne pédagogique centrale est :

```text
Référentiel
-> extraction niveau-classe
-> JSON canonique de référentiel niveau-classe
-> compétences
-> critères observables
-> scénario pédagogique
-> starter Welcome (source réutilisable)
-> séquence pédagogique
-> séances pédagogiques
-> contenus de la séance (dossier technique, QCM de compréhension, checklist, travail pratique...)
-> affectation à une classe ou à un élève (fige un instantané de la séquence, ADR-026)
-> progression élève
-> suivi professeur
-> évaluation par critères
-> bilan professeur
```

Règles pédagogiques fortes :

- le référentiel officiel donne le cadre ;
- le JSON canonique niveau-classe formalise la partie réellement exploitée pour une classe ou un niveau ;
- le scénario pédagogique définit l'intention ;
- le starter Welcome est une source réutilisable d'où l'on crée une séquence (trace de provenance, §4) ;
- la séquence pédagogique organise le travail élève ;
- l'affectation transforme une séquence publiée en travail réel pour une classe ou un élève, et en fige un instantané (ADR-026) ;
- la séance découpe la séquence en unités de travail ordonnées ;
- le dossier technique apporte les connaissances nécessaires ;
- le QCM vérifie la compréhension du dossier technique ;
- le QCM ne valide pas une compétence ;
- la séance est le lieu de réalisation du travail et d'observation des compétences (l'ancien objet « activité » autonome est fondu dans la séance) ;
- l'évaluation des compétences se fait dans la séance, à partir de critères observables ;
- la checklist guide l'élève et le professeur ;
- la progression garde l'état réel de l'élève ;
- le suivi professeur permet d'identifier les élèves bloqués, en avance ou à évaluer.

> Révision (2026-07-19) : vocabulaire aligné sur l'ADR-025 (Séquence / Séance) ; fusion de l'objet « activité » dans la séance et versionnement par instantané à l'affectation actés par l'ADR-026. Le « starter Welcome » n'est **pas** un objet métier (table supprimée, ADR-022) : c'est une **source réutilisable** d'où l'on crée une séquence, dont la provenance sera tracée par un champ ajouté avec SEQ-02.

## 13. Méthode de construction

Ne pas commencer par coder les interfaces finales.

Ne pas commencer par un grand diagramme de classes global.

Commencer par une fonctionnalité métier évidente ou par une source canonique nécessaire à cette fonctionnalité.

Ordre général :

1. identifier la source originelle ;
2. tracer la provenance ;
3. produire ou compléter le JSON canonique ;
4. produire ou enrichir le dictionnaire de données ;
5. écrire les règles métier ;
6. écrire le cycle de vie ;
7. déduire le modèle relationnel ;
8. déduire le diagramme de classes ;
9. déduire le contrat d'entité Forge ;
10. créer la migration SQL ;
11. créer le repository ;
12. créer le service métier ;
13. créer l'interface métier ;
14. écrire les tests.

## 14. Premiers jalons

Le premier jalon documentaire et source doit installer la chaîne de sources :

- référentiel officiel Bac Pro CIEL ;
- fichier `.scpro` CPRO ;
- fichier `.odt` exporté depuis CPRO ;
- trace de création du JSON canonique ;
- JSON canonique CIEL 2TNE ;
- schéma JSON associé ;
- dictionnaire de données généré ou prérempli.

Le premier jalon métier applicatif doit ensuite installer la chaîne Scenario :

- créer ou importer un scénario pédagogique à partir d'une source ou d'un JSON canonique ;
- créer le dictionnaire de données `Scenario` ;
- créer les règles métier `Scenario` ;
- créer le cycle de vie `Scenario` ;
- déduire le modèle relationnel `Scenario` ;
- déduire le diagramme de classes `Scenario` ;
- déduire le contrat d'entité Forge `Scenario` ;
- créer la migration SQL `Scenario` ;
- créer le repository `Scenario` ;
- créer le service `Scenario` ;
- créer une interface professeur minimale pour créer, consulter, modifier et publier un scénario ;
- tester la persistance du scénario.

Le premier jalon ne doit pas créer de parcours fichier comme source principale.

## 15. Objets métier principaux

Objets principaux à prévoir :

- SourceDocument ;
- JSONCanonique ;
- SchemaJSONCanonique ;
- Formation ;
- NiveauClasse ;
- Référentiel ;
- VersionRéférentiel ;
- VueRéférentielNiveauClasse ;
- PôleActivité ;
- ActivitéProfessionnelle ;
- TâcheProfessionnelle ;
- RésultatAttendu ;
- Compétence ;
- CritèreObservable ;
- IndicateurRéussite ;
- NiveauAcquisition ;
- Scenario ;
- SequencePedagogique ;
- SeancePedagogique ;
- ElementSeance (composition ordonnée de la séance, jalon SEQ-03) ;
- InstantaneAffectation (copie figée d'une séquence, ADR-026) ;
- DocumentTechnique ;
- QCM ;
- QuestionQCM ;
- ChoixQCM ;
- Checklist ;
- ItemChecklist ;
- Affectation ;
- Progression ;
- ÉvaluationSéance ;
- ÉvaluationCritère ;
- Ressource ;
- DépôtÉlève.

## 16. Séparation obligatoire entre définition et exécution

Définition pédagogique :

- référentiel ;
- vue de référentiel niveau-classe ;
- compétence ;
- critère ;
- indicateur de réussite ;
- scénario ;
- séquence ;
- séance ;
- dossier technique ;
- QCM ;
- checklist ;
- règle de passage.

Exécution élève :

- affectation ;
- progression ;
- tentative QCM ;
- réponse QCM ;
- checklist remplie ;
- dépôt élève ;
- validation professeur ;
- évaluation ;
- observation ;
- bilan.

Règle forte :

```text
Une séquence publiée et affectée ne doit pas changer sous les pieds d'un élève (figée par instantané à l'affectation, ADR-026).
```

## 17. Versionnement

Un objet pédagogique publié ne doit pas être modifié librement s'il est déjà utilisé.

On fige un instantané de la séquence à l'affectation ; l'exécution élève référence cet instantané, jamais la définition vivante (ADR-026). « Finalisé » n'est pas un statut : c'est un indicateur de complétude dérivé des données.

Statuts à prévoir :

```text
brouillon
publie
archive
```

Le figeage se fait par **instantané à l'affectation** (ADR-026), pas par des objets `Version*` explicites (écartés pour l'instant). Une séquence non affectée reste librement éditable ; une fois affectée, son instantané est immuable et porte l'exécution élève.

## 18. Architecture attendue

Règles d'architecture :

- les contrôleurs ne contiennent pas la logique métier ;
- les templates ne calculent pas la progression ;
- les services métier restent indépendants du détail des opt-ins ;
- les repositories isolent l'accès à la base ;
- les opt-ins Forge sont appelés via des façades ;
- les contrats d'entités Forge sont dérivés du dictionnaire de données ;
- les migrations SQL sont dérivées du dictionnaire de données ;
- le diagramme de classes est dérivé du dictionnaire de données, pas inventé séparément.

Structure logique conseillée :

```text
app/domain/identity
app/domain/school
app/domain/sources
app/domain/referential
app/domain/scenario
app/domain/starter
app/domain/learning
app/domain/assessment
app/domain/tracking
app/domain/communication
app/services
app/infrastructure/database
app/infrastructure/repositories
app/infrastructure/migrations
app/infrastructure/seeds
app/infrastructure/filesystem
app/infrastructure/optins
app/web/public
app/web/auth
app/web/student
app/web/teacher
app/web/admin
```

Dossiers documentaires conseillés :

```text
docs/cadrage
docs/specs/json-canonique
docs/specs/json-canonique/traces
docs/specs/json-canonique/schemas
docs/specs/json-canonique/examples
docs/specs/data-dictionary
docs/specs/business-rules
docs/specs/lifecycle
docs/specs/relational-model
docs/specs/class-diagrams
docs/specs/entity-contracts
docs/architecture
docs/tickets
docs/archive
```

## 19. Rôles et permissions

Rôles minimaux :

- eleve ;
- professeur ;
- administrateur.

Permissions minimales élève :

- `eleve.voir_ses_parcours` ;
- `eleve.voir_sa_progression` ;
- `eleve.repondre_qcm` ;
- `eleve.remplir_checklist` ;
- `eleve.deposer_travail`.

Permissions minimales professeur :

- `professeur.voir_classes` ;
- `professeur.gerer_eleves` ;
- `professeur.creer_scenario` ;
- `professeur.creer_starter` ;
- `professeur.creer_parcours` ;
- `professeur.affecter_parcours` ;
- `professeur.evaluer_activites` ;
- `professeur.valider_paliers` ;
- `professeur.voir_progression_classe`.

Permissions minimales administrateur :

- `admin.gerer_utilisateurs` ;
- `admin.gerer_roles` ;
- `admin.gerer_referentiels` ;
- `admin.gerer_sources` ;
- `admin.gerer_parcours` ;
- `admin.gerer_systeme`.

## 20. Sécurité

Règles fortes :

- un élève ne voit que ses propres parcours ;
- un professeur ne voit que ses classes ou les classes autorisées ;
- les ressources professeur restent protégées ;
- les accès directs par URL doivent être contrôlés ;
- un QR code ne doit jamais contourner les droits ;
- les comptes professeur et administrateur doivent pouvoir utiliser la MFA.

## 21. Opt-ins Forge

Règle :

```text
Les opt-ins servent le métier.
Le métier ne doit pas dépendre directement du détail des opt-ins.
```

Opt-ins critiques envisagés :

- forge facades ;
- forge rbac ;
- forge mfa ;
- forge markdown ;
- forge fichier ;
- forge pivot ;
- forge admin.

Opt-ins utiles :

- forge image ;
- forge qrcode ;
- forge notification ;
- forge mail.

Opt-ins à repousser si nécessaire :

- forge video ;
- forge search ;
- forge cache ;
- forge export / pdf ;
- statistiques avancées ;
- messagerie complète.

## 22. Interdits de dérive

Ne pas proposer une V0 fichier.

Ne pas créer `path.yml`, `palier.yml`, `qcm.yml` ou `checklist.yml` comme base principale du projet.

Ne pas confondre JSON canonique et simple fichier de parcours.

Ne pas confondre JSON canonique de référentiel niveau-classe et scénario pédagogique.

Ne pas confondre résultats attendus, critères d'évaluation et indicateurs de réussite.

Ne pas confondre QCM et compétence.

Ne pas remplacer l'espace professeur par un simple back-office admin.

Ne pas modifier une séquence publiée et affectée : elle est figée par instantané à l'affectation (ADR-026).

Ne pas exposer les ressources professeur à l'élève.

Ne pas élargir le périmètre d'un ticket sans validation.

## 23. Règles de réponse et de tickets

Répondre en français.

Être clair, direct et critique.

Signaler les contradictions et les risques de dérive.

Travailler par tickets limités.

Pour les tickets destinés à Claude Code ou Codex, inclure obligatoirement :

- objectif ;
- périmètre autorisé ;
- hors périmètre ;
- boucle de travail obligatoire ;
- test prémortem ;
- critères de validation.

Quand un document est demandé, fournir si possible un fichier Markdown téléchargeable.
