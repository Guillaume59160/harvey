# Pilote Étatloc — protocole de validation sans prospection active

Configuration initiale : [`pilots/etatloc/harvey.yaml`](./harvey.yaml). **Ne jamais copier sur un conteneur qui envoie déjà des emails.** L'adresse .example est fictive.

## Critères
- Zéro envoi email, zéro message ou invitation LinkedIn et zéro accès à une messagerie réelle.
- Uniquement des entreprises et informations professionnelles publiques pour une phase ultérieure; commencer avec des entreprises fictives.
- Revue de la qualité de 10 à 20 fiches *à la main* avant tout export.
- Aucun scraping des coordonnées privées, collecte sensible ou import automatique dans EspoCRM.
- Les fonctions qui exigent une validation d'expéditeur/une API externe restent désactivées.

## Parcours de test
1. Valider les derniers tests CI sur le commit exact déployé, puis Docker et pare-feu en environnement **isolé**.
2. Copier ce `harvey.yaml` dans une copie jetable du dépôt (ne pas écraser le fichier racine).
3. Vérifier que les deux canaux sont désactivés et que `max_daily_sends: 0`.
4. Charger une dizaine de fiches d'entreprises **fictives** et des descriptions synthétiques dans l'environnement d'essai. Ne pas donner de faux résultats pour des entreprises réelles.
5. Tester les vues de qualification, la cohérence des segments et les brouillons de messages. Vérifier le retour en lecture seule et l'export CSV hors EspoCRM.
6. Réaliser un audit manuel des données, des traces et des suppressions; documenter chaque faux positif.
7. Lorsque la partie technique est validée, étudier un échantillon restreint d'entreprises publiques du Nord, sans expédier d'emails.

## Tableau de décision
| Mesure | Cible pilote |
|---|---|
| Messages réellement expédiés | 0 |
| Connexions aux outils métier de production | 0 |
| Fiches examinées manuellement | 10 à 20 |
| Données de contact sensibles/non pertinentes | 0 |
| Fiabilité des champs et sources | Vérification individuelle |
| CSV importé automatiquement dans EspoCRM | Non |

## Intégration prévue
EspoCRM : créer plus tard un connecteur *avec prévisualisation et validation humaine*, identifiants externes et dédoublonnage. Hermes : ne déclencher que des opérations explicitement autorisées. Isoler les données de chaque société.

## Limites
La configuration n'active pas un mode `dry-run` universel. Les commandes de recherche, d'entraînement et de découverte peuvent consulter des sites ou facturer des API. Les essais sans egress doivent utiliser des simulations/local mocks. Vérifier les obligations RGPD avant un pilote sur de vraies personnes.
