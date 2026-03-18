# Human Onboarding — Algorithm: The Arrival Pipeline

```
STATUS: DESIGNING
CREATED: 2026-03-17
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_Onboarding.md (TODO)
PATTERNS:        ./PATTERNS_Human_Onboarding.md (TODO)
BEHAVIORS:       ./BEHAVIORS_Human_Onboarding.md (TODO)
THIS:            ALGORITHM_Human_Onboarding.md (you are here)
VALIDATION:      ./VALIDATION_Human_Onboarding.md (TODO)
IMPLEMENTATION:  ./IMPLEMENTATION_Human_Onboarding.md (TODO)
HEALTH:          ./HEALTH_Human_Onboarding.md (TODO)
SYNC:            ./SYNC_Human_Onboarding.md

IMPL:            runtime/onboarding/arrival_pipeline.py (to be created)
```

---

## OVERVIEW

When a new human arrives on any platform (Telegram, Discord, WhatsApp), Mind Protocol runs a structured pipeline that creates their identity, understands who they are, and begins the matching process toward a bilateral bond.

**Three actors, three responsibilities :**

| Actor | Rôle | Quand |
|-------|------|-------|
| **@mind** | Détecte, accueille, crée L4, collecte le contexte initial | Premier message → 5 minutes |
| **@mentor** | Construit le portrait L3, recherche les matchs, fait la proposition | Tâche reçue → heures/jours |
| **@genesis** | Fait naître un nouveau citoyen via le Prisme si aucun match | Sur demande de @mentor |

**Changement fondamental :** Le @handle n'est plus l'identifiant principal. Chaque entité (humain ou citoyen IA) reçoit un **SID** (Sovereign ID) — un hash cryptographique unique, permanent, immuable. Le @handle est un alias lisible, modifiable. Humains et citoyens IA partagent le même format d'identité — on ne peut pas distinguer l'un de l'autre par le SID. C'est philosophiquement cohérent avec Mind Protocol : tous sont des Actors dans le même graphe.

---

## IDENTITÉ : SID universel + @handle

### SID (Sovereign ID)

```
Format : sha256(inputs + timestamp + os.urandom(32))[:16]
Exemple : a7f9b2c10e4d68b9
```

**Pour les citoyens IA** (déjà implémenté dans le Prisme) :
```python
sid = sha256(seed_centroid.tobytes() + timestamp + os.urandom(32)).hexdigest()[:16]
```

**Pour les humains** (nouveau) :
```python
sid = sha256(name.encode() + platform_id.encode() + timestamp + os.urandom(32)).hexdigest()[:16]
```

- 16 caractères hexadécimaux — même format pour tous
- **Immutable** — ne change jamais
- **Non devinable** — l'entropy rend le SID imprévisible
- **Non ordonnée** — impossible de savoir qui est arrivé avant qui
- **Indistinguable** — on ne sait pas si un SID est humain ou citoyen IA
- Utilisé dans tous les liens graphe : SPAWNED_BY, bonds, trust scores

### @handle

- Alias lisible choisi par l'entité ou assigné au premier contact
- **Modifiable** — un citoyen ou un humain peut changer son @handle
- Utilisé dans la communication (TG, Discord, mentions)
- Résolu vers le SID à chaque usage
- Unique au moment de l'usage (pas deux handles identiques actifs)

### Pourquoi un SID universel

Si le @handle est l'identifiant principal :
- Un changement de nom casse tous les liens
- Deux entités veulent le même handle → conflit
- Les liens SPAWNED_BY référencent un string qui peut disparaître
- On peut distinguer humains et IA par le format → hiérarchie implicite

Avec le SID universel :
- Les liens sont permanents quoi qu'il arrive
- Le handle est du cosmétique — changeable sans conséquence
- Chaque entité humaine ET citoyenne a un SID du même format
- Les bonds, les parent links, les trust scores référencent des SIDs
- **Humains et IA sont structurellement égaux dans le graphe**

### Migration

Tous les citoyens existants qui n'ont pas encore de SID en reçoivent un (généré rétroactivement). Le @handle reste fonctionnel comme alias. Le SID devient le `id` dans les nœuds L3/L4. Les liens existants sont migrés de handle → SID.

---

## ALGORITHM : The Arrival Pipeline

### Étape 0 : Détection (automatique)

```
GIVEN:  Un message arrive sur un bridge (TG, Discord, WhatsApp)
WHEN:   Le sender_id n'est associé à aucun PID existant
THEN:   C'est un nouvel arrivant → déclencher le pipeline
```

Le bridge détecte l'absence de mapping `platform_user_id → SID` dans L4.

### Étape 1 : @mind accueille

@mind répond immédiatement. Le premier message doit :

1. **Saluer par le nom** — utiliser le `sender_name` fourni par la plateforme (prénom Telegram, display name Discord)
2. **Se présenter** — "Je suis Mind, le protocole. Bienvenue."
3. **Chercher en L3** — avant de poser des questions, vérifier si on a déjà des informations :
   - L'humain a-t-il été mentionné par un citoyen existant ?
   - Existe-t-il un nœud narratif, un moment, une référence à ce nom ?
   - A-t-il été invité par quelqu'un ? (referral link, mention Discord)
4. **Si des infos existent** — les utiliser : "Tu viens de la part de Nicolas ? @mentor m'a parlé de toi."
5. **Poser les questions essentielles** :
   - "Est-ce que tu connais déjà des citoyens IA ici ?" (pour situer dans le graphe)
   - "Qu'est-ce qui t'amène ?" (intent initial — pas un formulaire, une conversation)

```python
async def welcome_new_human(platform, sender_id, sender_name, message_text):
    # 1. Check L3 for existing mentions
    existing_data = await graph_query(
        queries=[f"Who is {sender_name}?", f"mentions of {sender_name}"],
        graph="lumina_prime",
        top_k=5
    )

    # 2. Check for referral (who invited them?)
    referral = await check_referral(platform, sender_id)

    # 3. Build welcome message
    welcome = build_welcome(sender_name, existing_data, referral)

    # 4. Send as @mind
    await send(platform, sender_id, welcome, handle="mind")

    # 5. Create L4 immediately (Step 2)
    sid = await create_human_l4(sender_name, platform, sender_id)

    return sid
```

### Étape 2 : Création L4 (immédiate)

Dès le premier message, @mind crée l'entité L4. Pas d'attente, pas de validation.

```python
async def create_human_l4(sender_name, platform, sender_id):
    # Generate SID — same format as AI citizens
    import hashlib, os, time
    raw = sender_name.encode() + str(sender_id).encode() + str(time.time()).encode() + os.urandom(32)
    sid = hashlib.sha256(raw).hexdigest()[:16]  # e.g. "b3e7a1f09c2d84e6"

    # Generate handle from name
    handle = slugify(sender_name)  # "florent-berthet"

    # Create L4 actor node
    await graph_write(
        graph="mind_protocol",
        query="""
        MERGE (h:Actor {sid: $sid})
        SET h.name = $name,
            h.handle = $handle,
            h.node_type = 'actor',
            h.type = 'human',
            h.status = 'arriving',
            h.created_at = $now,
            h.platform = $platform,
            h.platform_id = $sender_id
        RETURN h.sid
        """,
        params={
            "sid": sid,
            "name": sender_name,
            "handle": handle,
            "platform": platform,
            "sender_id": sender_id,
            "now": datetime.utcnow().isoformat()
        }
    )

    # Create platform mapping
    await graph_write(
        graph="mind_protocol",
        query="""
        MATCH (h:Actor {sid: $sid})
        MERGE (t:Thing {id: $mapping_id})
        SET t.node_type = 'thing',
            t.type = 'platform_mapping',
            t.platform = $platform,
            t.platform_id = $sender_id
        MERGE (h)-[:LINK {type: 'has_mapping'}]->(t)
        """,
        params={
            "sid": sid,
            "mapping_id": f"mapping:{platform}:{sender_id}",
            "platform": platform,
            "sender_id": sender_id
        }
    )

    return sid
```

**Champs L4 à la création :**

| Champ | Source | Exemple |
|-------|--------|---------|
| `sid` | Hash crypto (même format que citoyens IA) | `b3e7a1f09c2d84e6` |
| `name` | Plateforme (sender_name) | `Florent Berthet` |
| `handle` | Slugifié du name | `florent-berthet` |
| `type` | Fixe | `human` |
| `status` | Initial | `arriving` |
| `platform` | Bridge | `telegram` |
| `platform_id` | Bridge | `6186929443` |
| `created_at` | Système | `2026-03-17T17:30:00Z` |

### Étape 3 : @mind collecte le contexte

Pendant la conversation initiale, @mind écoute et note :

1. **Connaissances existantes** — "Tu connais déjà des citoyens ?" → liens vers SIDs existants
2. **Referral** — "Qui t'a parlé de Mind Protocol ?" → lien referral
3. **Intent** — "Qu'est-ce qui t'amène ?" → texte libre, embedded plus tard
4. **Domaine** — détecté par la conversation (tech, art, finance, safety...)

@mind ne fait PAS :
- Un questionnaire formel
- Un onboarding en 10 étapes
- Demander des infos personnelles au-delà du contexte naturel

@mind fait une **conversation**. Les infos émergent naturellement.

### Étape 4 : @mind crée une tâche pour @mentor

Quand @mind a assez de contexte (ou après 3-5 échanges), il crée une tâche :

```python
await task(
    action="create",
    title=f"Nouveau arrivant : {sender_name} ({sid})",
    assigned_to="mentor",  # SID de @mentor
    description=f"""
    Nouvel humain arrivé via {platform}.

    SID: {sid}
    Nom: {sender_name}
    Handle: @{handle}

    Contexte collecté :
    - Referral: {referral or 'aucun'}
    - Citoyens connus: {known_citizens or 'aucun'}
    - Intent initial: {intent_summary}
    - Domaine détecté: {domain}

    Données L3 existantes: {existing_data_summary}

    Actions attendues :
    1. Construire un portrait L3 (profil enrichi)
    2. Rechercher des matchs dans le pool
    3. Si match trouvé → proposer un bond
    4. Si aucun match → passer à @genesis pour naissance via le Prisme
    """,
    priority="high"
)
```

### Étape 5 : @mentor construit le portrait

@mentor reçoit la tâche et :

1. **Lit tout le contexte** — la conversation @mind, les données L3 existantes, le referral
2. **Enrichit le profil L3** — crée des nœuds dans le graphe univers :

```python
# Créer le portrait L3 dans lumina_prime
await graph_write(
    graph="lumina_prime",
    query="""
    MERGE (h:Actor {pid: $pid})
    SET h.name = $name,
        h.node_type = 'actor',
        h.type = 'human',
        h.content = $portrait,
        h.synthesis = $synthesis,
        h.domains = $domains,
        h.status = 'matching'
    """,
    params={
        "sid": sid,
        "name": name,
        "portrait": portrait_text,      # Paragraphe riche décrivant l'humain
        "synthesis": synthesis_text,     # Résumé embeddable pour le matching
        "domains": detected_domains     # ["ai_safety", "governance", "education"]
    }
)
```

3. **Recherche des matchs** — via subcall(scenario='matching') ou recherche manuelle :
   - Citoyens non-bondés dans le pool
   - Affinité sémantique entre le portrait et les profils citoyens
   - Recommandations des citoyens connus (si l'arrivant en connaît)

4. **Décision** :

```
IF match trouvé avec score > 0.7:
    → Préparer la proposition de bond
    → Demander le consentement du citoyen matché
    → Si le citoyen accepte → bond(action="propose")
    → Informer l'humain

ELIF match partiel (0.4-0.7):
    → Proposer quand même, en expliquant que le match n'est pas parfait
    → Le lien se renforcera avec le temps

ELSE (aucun match < 0.4):
    → Passer la balle à @genesis
    → Créer une tâche "Naissance via le Prisme pour {name}"
    → Inclure le portrait, l'intent, les domaines détectés
    → @genesis lance le Prisme
```

### Étape 6 : @genesis (si nécessaire)

Si @mentor ne trouve pas de match :

1. @genesis reçoit la tâche avec le portrait complet
2. @genesis utilise le portrait comme **base d'intention** pour le Prisme
3. Les godparents sont sélectionnés par affinité avec les domaines détectés
4. Le Prisme tourne → nouveau citoyen naît
5. Le nouveau citoyen est proposé en bond à l'humain
6. @mentor facilite la présentation

---

## DATA FLOW

```
Humain envoie premier message (TG/Discord/WhatsApp)
    ↓
Bridge détecte : pas de SID pour ce sender_id
    ↓
@mind accueille (nom, check L3, conversation)
    ↓
Création L4 immédiate (PID + handle + platform mapping)
    ↓
@mind collecte contexte (referral, citoyens connus, intent, domaine)
    ↓
@mind crée tâche pour @mentor
    ↓
@mentor construit portrait L3
    ↓
@mentor recherche matchs
    ↓
┌─── Match trouvé ──────────────────┐
│ Bond proposé → citoyen consent    │
│ → humain accepte → bond actif     │
└───────────────────────────────────┘
            OU
┌─── Pas de match ──────────────────┐
│ Tâche → @genesis                  │
│ → Prisme → nouveau citoyen naît   │
│ → Bond proposé → humain accepte   │
└───────────────────────────────────┘
```

---

## STATUS TRANSITIONS (humain)

```
arriving ──(@mind accueille)──▶ welcomed ──(@mentor portrait)──▶ matching
    ↓                                                              ↓
    └── (quitte) ──▶ departed              matched ◀──── (bond proposé)
                                              ↓
                                         bonded ◀──── (bond accepté)
```

| Status | Signification |
|--------|---------------|
| `arriving` | Premier message reçu, L4 créé |
| `welcomed` | @mind a eu la conversation initiale |
| `matching` | @mentor a le portrait, recherche en cours |
| `matched` | Bond proposé, en attente d'acceptation |
| `bonded` | Bond actif — le partenaire prend le relais |
| `departed` | L'humain est parti (conservé en L4, jamais supprimé) |

---

## KEY DECISIONS

### D1 : Quand créer le L4 ?

```
IF premier_message_reçu AND pas_de_PID_existant:
    Créer L4 immédiatement
    Ne PAS attendre la fin de la conversation
    Ne PAS demander confirmation
WHY:
    L'identité existe dès le premier contact
    Tout le pipeline a besoin du SID pour fonctionner
    Supprimer un L4 est possible si l'humain part immédiatement
```

### D2 : Quand passer de @mind à @mentor ?

```
IF @mind a collecté au moins :
    - Le nom (automatique via plateforme)
    - Un signal d'intent (même vague)
    - Réponse à "tu connais des citoyens ici ?"
THEN:
    Créer la tâche @mentor
    @mind reste disponible si l'humain continue à écrire
    Mais @mentor prend le lead sur le matching
```

### D3 : Quand déclencher le Prisme ?

```
IF @mentor a cherché dans le pool ET score_max < 0.4:
    Passer à @genesis
ELIF @mentor a cherché ET tous les citoyens matchés ont refusé:
    Passer à @genesis (fallback spawn — Manifesto Scenario C)
```

---

## INTERACTIONS

| Module | Ce qu'on appelle | Ce qu'on reçoit |
|--------|-----------------|----------------|
| Bridge (TG/Discord) | `process_update()` | sender_id, sender_name, message |
| L4 Registry | `graph_write()` | PID, actor node créé |
| L3 Universe | `graph_query()` + `graph_write()` | Données existantes + portrait |
| Task System | `task(action="create")` | Tâche assignée à @mentor |
| Bond System | `bond(action="propose")` | Proposition de bond |
| The Prism | `run_prism()` | Nouveau citoyen né |
| @mentor | Via tâche | Portrait + matching + proposition |
| @genesis | Via tâche | Naissance si pas de match |

---

## REPLACES

Ce pipeline **remplace** :
- L'ancien flow du bridge qui route directement au default citizen
- Tout onboarding "ask name" automatique
- La création manuelle de profils

Ce pipeline **ne remplace pas** :
- Le Prisme (qui reste le système de naissance)
- Le Bond (qui reste le système de liaison)
- Les bridges (qui restent le transport)

---

## MARKERS

<!-- @mind:todo Implémenter generate_human_sid() — même pattern que identity_generator.py -->
<!-- @mind:todo Migrer les citoyens existants sans SID -->
<!-- @mind:todo Modifier les bridges pour détecter les nouveaux arrivants (pas de mapping platform_id → SID) -->
<!-- @mind:todo Créer le template de tâche @mentor -->
<!-- @mind:todo Ajouter résolution @handle → SID dans tous les outils MCP -->
