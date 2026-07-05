# ADR-008 — Import des JSON canoniques niveau-classe par upload dans l'admin (importeur générique)

## Statut

Accepté (2026-07-06).

> Décision validée par le porteur : **un niveau-classe entre dans l'application par
> upload d'un JSON canonique dans l'espace admin** (importeur générique), pas en dur
> dans le dépôt. Élève le schéma (ticket 04) au rang de priorité.

## Date

2026-07-05

## Contexte

Le JSON canonique est la **référence structurée de construction ou d'import**
(ADR-002) ; la **base** est la vérité applicative en fonctionnement. Reste à décider
**comment** un référentiel niveau-classe (ex. CIEL 2TNE) devient exploitable dans
l'application.

Deux options :

- **(a)** Produire à la main, dans le dépôt, un JSON canonique par classe, puis le
  charger au déploiement. Rigide : ajouter une classe suppose de toucher au dépôt.
- **(b)** L'**administrateur uploade** le JSON canonique de *n'importe quel*
  niveau-classe ; l'application le **valide** puis l'**importe** en base.

Le porteur retient **(b)**.

## Décision

1. **Upload en admin.** L'espace **admin** de l'application expose une fonction
   « **ajouter un niveau-classe par upload de son JSON canonique** ».

2. **Valider puis importer.** À l'upload : (1) **validation** du fichier contre le
   **schéma JSON** (ticket 04) — un fichier non conforme est refusé avec un message
   clair ; (2) **construction et persistance** des objets métier en base (formation,
   niveau_classe, pôles, activités + tâches/résultats attendus, compétences +
   critères, indicateurs, relations), avec leur **provenance**.

3. **Importeur générique.** Aucune classe n'est codée en dur : l'application importe
   *tout* JSON canonique conforme au contrat. Le **discriminant `type`** de
   l'enveloppe (contrat, ticket 02) route l'import : `referentiel_niveau_classe`
   aujourd'hui, `starter_welcome` demain.

4. **La base reste la vérité** (ADR-002). Après import, les objets vivent en base.
   Le **fichier uploadé est conservé** comme trace de provenance (source), il ne
   redevient pas l'état applicatif.

5. **Sécurité et opt-ins.** Fonction **réservée aux administrateurs** (rôle `admin`,
   RBAC le moment venu). Briques Forge mobilisées : `forge-mvc-admin` (espace admin),
   `forge-mvc-files` (upload), plus les entités, migrations et l'importeur. Backend
   MariaDB (ADR-004).

## Conséquences

- Le **schéma JSON (ticket 04) devient central et prioritaire** : c'est la porte de
  validation des uploads.
- Le **JSON canonique CIEL 2TNE (ticket 03)** devient un **exemple / fixture** — le
  premier payload à uploader et un support de test — plutôt qu'un livrable en soi.
- **Généricité** : ajouter une classe = uploader son JSON, sans redéploiement ni
  code spécifique.
- La chaîne **upload → valider → importer → persister** est du **code applicatif**
  (à faire **ensemble**, tickets de programmation), et nécessite MariaDB + les
  opt-ins admin/files.
- L'enveloppe commune + discriminant `type` (ticket 02) est confirmée comme le bon
  point de généricité.

## Alternatives écartées

- **JSON hardcodé/fixture par classe** dans le dépôt : rejeté — non extensible par
  l'admin/le professeur sans intervention sur le code.
- **Import direct d'un export CPRO en base** sans passer par un JSON canonique
  contrôlé : rejeté (règle de la capitalisation `.scpro`, §9).

## Suite

- Prioriser le **ticket 04 (schéma JSON)** : la validation d'upload en dépend.
- Produire un **exemple CIEL 2TNE** conforme (fixture d'upload et de test).
- Définir les **tickets de la fonctionnalité admin upload/import** (programmation,
  à faire ensemble) : entités, migrations, importeur, écran admin d'upload.
