# Documentation - Spotiapp

#

# Exécution des tests

## Test de connexion au serveur

Se placer à la racine.

```zsh
uv run pytest
```

Le test est censé passer sans erreur. Si le test remonte une erreur ou ne termine pas, l'IP attribuée au serveur a probablement changée. Dans ce cas:

1. Vérifier que le container est bien actif (ouvrir un terminal Ubuntu et run `docker ps`)
2. Vérifier l'IPv4 du serveur (ouvrir un terminal PowerShell et run `ipconfig` puis prendre l'IPv4 de la carte Wi-Fi)
3. Si l'IP a changé, mettre à jour le `.env`.

# Exécution du code

## Mise à jour de l'architecture de BDD

Se placer dans `src/spotiapp`.

```zsh
uv run -m main update-db  {*chemin_relatif_depuis_la_racine_vers_le_script_de_maj*}
```

## Mise à jour du contenu de la BDD

Se placer dans `src/spotiapp`.

```zsh
uv run -m main run
```

## Utilisation de dbt

Pour toutes les commandes, se placer dans `spotiapp_dbt`.

### Test

```zsh
uv run dbt test
```

### Compilation

```zsh
uv run dbt run
```

### Commande principale

```zsh
uv run dbt build
```

Cette commande effectue la compilation ainsi que tous les tests automatiquement.

# Schéma de la base de données

```mermaid
erDiagram
    %% ==========================================
    %% CATALOGUE MUSICAL (Les entités intrinsèques)
    %% ==========================================
    TRACKS {
        varchar(50) id PK
        varchar(255) name
        varchar(50) album_id FK
        int duration
        varchar(255) url
        boolean is_single
    }

    ALBUMS {
        varchar(50) id PK
        varchar(255) name
        varchar(255) url
        varchar(50) type
        varchar(255) cover
    }

    ARTISTS {
        varchar(50) id PK
        varchar(255) name
        varchar(255) url
    }

    PLAYLISTS {
        varchar(50) id PK
        varchar(255) name
        varchar(255) url
    }

    %% ==========================================
    %% CONTEXTE UTILISATEUR (Tes interactions)
    %% ==========================================
    LIKED_TRACKS {
        varchar(50) track_id PK, FK
        timestamp date_added
    }

    LISTENING_HISTORY {
        int id PK "Auto-incrémenté"
        varchar(50) track_id FK
        timestamp played_at
    }

    TRACK_PLAYLISTS {
        varchar(50) track_id PK, FK
        varchar(50) playlist_id PK, FK
    }

    %% ==========================================
    %% TABLES DE JONCTION (Relations N:M)
    %% ==========================================
    TRACK_ARTISTS {
        varchar(50) track_id PK, FK
        varchar(50) artist_id PK, FK
    }

    TRACK_TAGS {
        varchar(50) track_id PK, FK
        varchar(50) tag PK
    }

    %% ==========================================
    %% RELATIONS
    %% ==========================================
    ALBUMS ||--o{ TRACKS : "contient"
    TRACKS ||--o{ LIKED_TRACKS : "est enregistré dans"
    TRACKS ||--o{ LISTENING_HISTORY : "est écouté dans"
    TRACKS ||--o{ TRACK_PLAYLISTS : "est ajouté à"
    PLAYLISTS ||--o{ TRACK_PLAYLISTS : "contient"
    TRACKS ||--|{ TRACK_ARTISTS : "est composé par"
    ARTISTS ||--o{ TRACK_ARTISTS : "compose"
    TRACKS ||--o{ TRACK_TAGS : "possède"
```
