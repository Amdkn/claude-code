# aspace-claude-code-adapter — clean-room (D12)

**Clean-room, zéro copie.** Cet adapter est écrit de zéro depuis la spécification publique uniquement (README, CLAUDE.md, exemples de settings, README du mod `mods/telemetry` du dépôt de référence). **Aucun fichier amont n'a été copié, aucune ligne de code amont reprise, aucun module amont importé.** L'adapter ne contient que de la documentation d'interface et un faux local (stdlib Python seule).

## Pourquoi clean-room

L'amont `anthropics/claude-code` est **sans licence libre** : l'API GitHub rapporte `license: null` et le fichier `LICENSE.md` dit « © Anthropic PBC. All rights reserved. Use is subject to Anthropic's Commercial Terms of Service » — un avis propriétaire, pas une licence libre. Le design D-N048 (décision D4, variante D12) tranche : fork = **référence seule**, adaptation = **clean-room**, **repli suppression nommé**.

**Repli :** si Anthropic s'oppose à la référence ou si une licence apparaît qui l'exige, le fork `Amdkn/claude-code` est **supprimé**. L'adapter, œuvre propre d'A'Space, ne dépend d'aucun fichier amont et survit tel quel.

## Contenu

- `contract.json` — la spécification de l'interface publique documentée : commande `claude`, modes de permission (`auto`, `acceptEdits`, `default`), commande `/bug`, mentions `@claude`, clés de settings nommées dans les exemples, événements de télémétrie documentés (`telemetry.log`, `telemetry.mark`) et leurs interrupteurs (`DISABLE_TELEMETRY`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `DO_NOT_TRACK`), URL d'ingest documentée (faite constatée uniquement — **l'adapter ne l'appelle jamais**).
- `mock_claude.py` — faux local écrit de zéro (stdlib seule) : `--help`, `--version`, `status` (lit un settings JSON local dans un scratch, rapporte les clés documentées présentes et l'état des interrupteurs, localement, sans réseau).
- `smoke_test.py` — 6 checks (stdlib seule) : contrat valide, `--help`, `--version`, `status`, **zéro code réseau dans l'adapter**, **stdlib seule**.
- `README.md` — ce fichier.

## Jamais

- Invoquer le CLI amont ou un code amont quelconque.
- Copier un fichier amont ou reprendre une ligne de code amont.
- Faire un appel réseau (l'adapter n'a aucun code réseau — vérifié par le smoke test).
- Lire un identifiant, envoyer quoi que ce soit vers `api.anthropic.com` ou ailleurs.

## Surface

Contrat seul (§1.5 du design) : description d'interface + faux local. Aucune couture d'exécution vers le CLI amont — il n'y en a pas en clean-room, par construction.

## Télémétrie

Voir `claude-code-TELEMETRY-AUDIT.md` (domicile V5) : télémétrie réelle dans l'amont, documentée par l'amont (collecte d'usage et de conversations, ingest `api.anthropic.com/api/event_logging/v2/batch`, interrupteurs lus avant chaque lot). **Télémétrie zéro dans l'adaptation** : le contrat et son faux local n'émettent rien, par construction.
