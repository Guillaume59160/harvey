# Harvey — plan de pilote multi-activités (préproduction, France)
Statut: **plan de validation, aucun déploiement ni envoi autorisé**.
Ce document décrit les usages envisagés pour Étatloc, H Event Connect, Renfort,
H Event et Ekin. Il ne décrit pas des connecteurs déjà opérationnels.

## Phase 0 — sécurité (conditions obligatoires)
- Six jobs CI verts sur le **SHA courant** de la branche.
- Validation de la configuration Docker **fusionnée** avec
  `python scripts/check_security_compose.py` et Docker Compose.
- Test de l'isolation réseau depuis un conteneur de préproduction, sans
  accès aux services VPS existants, aux adresses privées ou aux métadonnées.
- Tests d'arrêt d'urgence avec fournisseurs simulés; aucune adresse réelle.
- Vérifier le domaine expéditeur, SPF/DKIM/DMARC et l'encadrement RGPD.
- Garder `channels.email.enabled: false` et `channels.linkedin.enabled: false`
  tant que le pilote n'est pas explicitement validé. Pas de credentials
  professionnels ni de données personnelles réelles en phase sandbox.

## Ordre des pilotes
| Priorité | Activité | Cible B2B | Proposition | Indicateur |
|---|---|---|---|---|
| 1 | Étatloc | Agences de gestion locative et conciergeries, Lille/HDF | EDL + documents + incidents/artisans | prospects pertinents et demandes de démo |
| 2 | H Event Connect | Dirigeants et RH d'entreprises de 20 à 150 salariés, HDF | Animation et mesure de la cohésion | réponses pertinentes et rendez-vous |
| 3 | Renfort | Hôtels/restaurants/traiteurs, Lille/HDF | Renfort de personnel ponctuel | contacts qualifiés |
| 4 | H Event | Entreprises et organisateurs, HDF | Prestations et animations événementielles | demandes de devis |
| 5 | Ekin | Éleveurs équins professionnels | Recherche de partenaires pilote | entretiens qualifiés |

Les catégories de prospection ne sont pas des assertions d'existence ou de
qualité de prospects. Vérifier les données produites manuellement.

## Parcours de découverte sans envoi
1. Démarrer localement / en environnement jetable, **sans accès au VPS de production**.
2. Utiliser des entreprises fictives ou des données publiques non personnelles pour les premières vérifications.
3. Configurer une seule activité, un seul segment et une zone géographique.
4. Examiner la proposition de signaux de Harvey et n'activer que les signaux
   nécessaires; vérifier leur fiabilité sur un petit échantillon.
5. Préparer les séquences comme **brouillons uniquement** et évaluer la
   personnalisation; aucune expédition automatique.
6. Exporter les sociétés en CSV, contrôler doublons, sources et données inutiles.
7. Consigner résultats, anomalies, faux positifs et coût réel par prospect.

## Intégrations futures — non implémentées
- **EspoCRM**: correspondance société/contact/opportunité/activité, identifiants
  externes, synchronisation idempotente et journal d'audit.
- **Hermes**: orchestration en lecture/écriture minimale, validation humaine avant
  actions de prospection, séparation des identités et des secrets.
- **Multi-sociétés**: données et expéditeurs isolés (pas seulement un filtre
  d'interface); autorisations distinctes et aucune mutualisation implicite des contacts.

## Conformité / gouvernance
La prospection B2B française implique une analyse de base légale, information,
pertinence de l'objet du message et dispositif d'opposition; revoir aussi les
conditions d'utilisation des sources et des fournisseurs. Ne pas collecter de
coordonnées privées, de données sensibles ou de données d'élevage nominatives
pour les essais. Prévoir durées de conservation, suppression et liste de
suppression (opt-out) partagée uniquement si son usage est légal et proportionné.

## Critères de décision (pilote)
- 0 email réel et 0 action LinkedIn pendant les essais techniques.
- 0 accès constaté aux services internes du VPS.
- Arrêt d'urgence: aucun nouvel appel de send dans les scénarios simulés
  lorsque l'arrêt est actif avant l'appel externe.
- Prospects: revue manuelle d'un échantillon et motifs de sélection documentés.
- Coûts et limites d'utilisation des abonnements CLI validés auprès du fournisseur.

## Important
Un arrêt local Harvey ne révoque pas les envois déjà pris en charge par
Instantly ou tout autre prestataire. Ces campagnes doivent être suspendues
chez le prestataire. La vérification pré-connexion DNS de l'anti-SSRF n'est
pas une protection réseau complète contre le DNS rebinding.
