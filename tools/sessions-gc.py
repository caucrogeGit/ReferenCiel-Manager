#!/usr/bin/env python3
"""Purge des sessions expirées (opt-in forge-mvc-sessions-db, comble F35).

Pourquoi ce script plutôt que `forge sessions:gc` : la commande CLI de l'opt-in
n'amorce pas la configuration du projet (env/dev) avant d'ouvrir la connexion,
donc elle échoue avec « Access denied ... (using password: NO) » hors d'un
serveur lancé (voir retour terrain 017). Ici on importe `config` d'abord, ce qui
charge l'environnement et les identifiants de base comme le fait `app.py`.

Usage manuel :
    .venv/bin/python tools/sessions-gc.py

Le script se replace lui-même dans la racine projet : cron/systemd n'ont donc
pas besoin de positionner le répertoire de travail, seuls les chemins absolus
suffisent.

Branchement cron (toutes les heures) :
    0 * * * * /chemin/vers/ReferenCiel-Manager/.venv/bin/python \
        /chemin/vers/ReferenCiel-Manager/tools/sessions-gc.py >> /var/log/sessions-gc.log 2>&1

Branchement systemd (timer) — sessions-gc.service + sessions-gc.timer :
    [Service]
    ExecStart=/chemin/vers/ReferenCiel-Manager/.venv/bin/python /chemin/vers/ReferenCiel-Manager/tools/sessions-gc.py
    [Timer]
    OnCalendar=hourly
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Le script vit dans tools/. On se place dans la racine projet AVANT d'importer
# config : celui-ci charge env/example et env/dev en chemins *relatifs*
# (load_dotenv("env/dev")), donc le CWD doit être la racine — sinon les
# identifiants DB ne sont pas chargés (c'est la cause même de F39). On ajoute
# aussi la racine à sys.path pour que `import config` résolve. Ainsi le script
# est robuste au répertoire d'appel (cron/systemd n'ont rien à positionner).
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    import config  # noqa: F401 — effet de bord : charge env/dev (identifiants DB)
    from forge_mvc_sessions_db import DbSessionStore

    removed = DbSessionStore().cleanup_expired()
    print(f"sessions expirées purgées : {removed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
