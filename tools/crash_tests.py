#!/usr/bin/env python
"""Crash tests HTTP de RéférenCiel Manager : robustesse face aux entrées adverses.

On n'attaque PAS la logique métier nominale (couverte par pytest) : on cherche à
faire tomber le serveur (500 non géré, stacktrace, épuisement de ressource) avec
des entrées forgées, des identifiants invalides, des jetons CSRF manquants, des
accès inter-rôles et une charge concurrente. Un 400/403/404/302 propre = OK ;
un 500 ou une exception = KO.

Nécessite un serveur en marche (`forge run`) ; ne dépend pas de pytest (il pilote
l'app par le réseau, pas en process). Les comptes sont ceux des fixtures de démo.

Usage :
    forge run &                                   # dans un terminal
    .venv/bin/python tools/crash_tests.py         # toutes les suites
    .venv/bin/python tools/crash_tests.py --base https://127.0.0.1:8010

Historique : la suite de concurrence a révélé l'épuisement du pool MariaDB sous
un pic « classe entière au login » (retour Forge 023) ; garder ce harnais permet
de rejouer le constat après tout réglage de `DB_POOL_SIZE` ou du backend.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from http.cookiejar import CookieJar
from typing import Any

BASE = "https://127.0.0.1:8010"

# Certificat auto-signé en dev : on ne vérifie pas la chaîne (test local).
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE

COMPTES = {
    "admin": ("admin@referenciel.local", "admin1234"),
    "prof": ("prof@referenciel.local", "prof1234"),
    "eleve": ("eleve@referenciel.local", "eleve1234"),
}

_ok = 0
_ko: list[str] = []


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a: object, **k: object) -> None:  # type: ignore
        return None


class Client:
    """Session HTTP (cookies persistés) avec extraction du jeton CSRF."""

    def __init__(self) -> None:
        self.jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar),
            urllib.request.HTTPSHandler(context=_CTX),
        )

    def get(self, path: str, *, redirect: bool = True) -> tuple[int, str]:
        return self._send("GET", path, None, redirect)

    def post(self, path: str, data: bytes | str, *, redirect: bool = False,
             ctype: str = "application/x-www-form-urlencoded") -> tuple[int, str]:
        body = data.encode() if isinstance(data, str) else data
        return self._send("POST", path, (body, ctype), redirect)

    def _send(self, method: str, path: str,
              payload: tuple[bytes, str] | None, redirect: bool) -> tuple[int, str]:
        url = path if path.startswith("http") else BASE + path
        headers = {"User-Agent": "crash-tester"}
        data = None
        if payload is not None:
            data, ctype = payload
            headers["Content-Type"] = ctype
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        opener = self.opener if redirect else urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar),
            urllib.request.HTTPSHandler(context=_CTX),
            _NoRedirect(),
        )
        try:
            resp = opener.open(req, timeout=15)
            return resp.getcode(), resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", "replace")

    def csrf(self, path: str) -> str:
        _, html = self.get(path)
        m = (re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
             or re.search(r'value="([^"]+)"[^>]*name="csrf_token"', html))
        return m.group(1) if m else ""

    def login(self, role: str) -> bool:
        email, pw = COMPTES[role]
        token = self.csrf("/login")
        body = urllib.parse.urlencode(
            {"csrf_token": token, "email": email, "password": pw})
        code, _ = self.post("/login", body, redirect=True)
        _, home = self.get("/login")
        return "password" not in home or code in (302, 303)


def check(nom: str, cond: bool, detail: str = "") -> None:
    global _ok
    if cond:
        _ok += 1
        print(f"  [OK]  {nom}")
    else:
        _ko.append(f"{nom} — {detail}")
        print(f"  [KO]  {nom} — {detail}")


def is_safe(code: int) -> bool:
    """Robuste = tout sauf une erreur serveur (5xx)."""
    return code < 500


# ── 1. Authentification : identifiants forgés / malformés ────────────────────

def suite_auth() -> None:
    print("\n== 1. Authentification (entrées forgées) ==")
    c = Client()
    token = c.csrf("/login")

    cas = {
        "email inexistant": {"email": "nobody@x.y", "password": "whatever"},
        "mot de passe vide": {"email": "admin@referenciel.local", "password": ""},
        "email vide": {"email": "", "password": "x"},
        "SQLi dans email": {"email": "' OR '1'='1", "password": "' OR '1'='1"},
        "email surdimensionné": {"email": "a" * 5000 + "@x.y", "password": "x"},
        "octets nuls": {"email": "admin\x00@x", "password": "x\x00"},
        "unicode/emoji": {"email": "🔥@💥.com", "password": "🧨" * 50},
    }
    for nom, champs in cas.items():
        body = urllib.parse.urlencode({"csrf_token": token, **champs})
        code, _ = c.post("/login", body)
        check(f"login {nom}", is_safe(code), f"HTTP {code}")

    # CSRF absent / invalide : refusé (403/302), jamais 500.
    body = urllib.parse.urlencode({"email": "admin@referenciel.local", "password": "admin1234"})
    code, _ = c.post("/login", body)
    check("login sans jeton CSRF", code in (400, 403, 302), f"HTTP {code}")
    body = urllib.parse.urlencode(
        {"csrf_token": "forge", "email": "admin@referenciel.local", "password": "admin1234"})
    code, _ = c.post("/login", body)
    check("login CSRF invalide", code in (400, 403, 302), f"HTTP {code}")

    # Corps non-form (JSON brut, binaire) sur une route form.
    code, _ = c.post("/login", b'{"email":"x"}', ctype="application/json")
    check("login corps JSON", is_safe(code), f"HTTP {code}")
    code, _ = c.post("/login", bytes(range(256)) * 4, ctype="application/octet-stream")
    check("login corps binaire", is_safe(code), f"HTTP {code}")


# ── 2. Contrôle d'accès : anonyme et inter-rôles ─────────────────────────────

def suite_acces() -> None:
    print("\n== 2. Contrôle d'accès (anonyme + inter-rôles) ==")
    protegees = [
        "/admin", "/conception/scenario", "/suivi", "/bilan",
        "/classe", "/sequence", "/mes-classes",
    ]
    anon = Client()
    for path in protegees:
        code, _ = anon.get(path, redirect=False)
        ok = code in (301, 302, 303, 401, 403, 404)
        check(f"anonyme bloqué sur {path}", ok, f"HTTP {code}")

    # Élève authentifié : pas d'accès à la conception ni à l'admin.
    eleve = Client()
    if eleve.login("eleve"):
        for path in ["/conception/scenario", "/admin"]:
            code, _ = eleve.get(path, redirect=False)
            ok = code in (301, 302, 303, 401, 403, 404)
            check(f"élève interdit sur {path}", ok, f"HTTP {code}")
    else:
        check("connexion élève", False, "login échoué")


# ── 3. Paramètres de route forgés (id) ───────────────────────────────────────

def suite_ids(role: str = "admin") -> None:
    print(f"\n== 3. Identifiants de route forgés (session {role}) ==")
    c = Client()
    if not c.login(role):
        check(f"connexion {role}", False, "login échoué")
        return
    gabarits = [
        "/conception/scenario/{}", "/conception/scenario/{}/pdf",
        "/sequence/show/{}", "/sequence/edit/{}",
        "/classe/show/{}", "/admin/scenario/{}",
    ]
    valeurs = ["0", "-1", "999999999", "abc", "1.5", "1e9", " ",
               "%00", "../../etc/passwd", "1;DROP TABLE",
               "9" * 40, "٢", "0x10", "null", "true"]
    for g in gabarits:
        for v in valeurs:
            path = g.format(urllib.parse.quote(v, safe=""))
            code, _ = c.get(path, redirect=False)
            check(f"GET {g} id={v!r}", is_safe(code), f"HTTP {code}")


# ── 4. POST forgés sur les actions d'écriture (avec CSRF valide) ─────────────

def suite_post_forges(role: str = "admin") -> None:
    print(f"\n== 4. POST forgés sur écritures (session {role}) ==")
    c = Client()
    if not c.login(role):
        check(f"connexion {role}", False, "login échoué")
        return

    token = c.csrf("/conception/scenario")
    cas = {
        "titre vide": {"titre": "", "referentiel_id": "1"},
        "referentiel inexistant": {"titre": "T", "referentiel_id": "999999"},
        "referentiel non-numérique": {"titre": "T", "referentiel_id": "abc"},
        "titre géant": {"titre": "T" * 10000, "referentiel_id": "1"},
        "titre XSS": {"titre": "<script>alert(1)</script>", "referentiel_id": "1"},
        "champ manquant": {"titre": "T"},
        "champ inattendu": {"titre": "T", "referentiel_id": "1", "hacker": "x"},
    }
    for nom, champs in cas.items():
        body = urllib.parse.urlencode({"csrf_token": token, **champs})
        code, _ = c.post("/conception/scenario/nouveau", body)
        check(f"POST nouveau — {nom}", is_safe(code), f"HTTP {code}")

    for sid in ["999999", "abc", "0"]:
        body = urllib.parse.urlencode({"csrf_token": token, "activite": "999999"})
        code, _ = c.post(f"/conception/scenario/{sid}/activite/basculer", body)
        check(f"POST basculer scénario={sid}", is_safe(code), f"HTTP {code}")

    # Écriture SANS jeton CSRF : refusée, jamais 500.
    body = urllib.parse.urlencode({"titre": "SansJeton", "referentiel_id": "1"})
    code, _ = c.post("/conception/scenario/nouveau", body)
    check("POST écriture sans CSRF", code in (400, 403, 302), f"HTTP {code}")


# ── 5. Surface HTTP : méthodes, chemins, en-têtes anormaux ───────────────────

def suite_http() -> None:
    print("\n== 5. Surface HTTP (méthodes/chemins/en-têtes) ==")
    c = Client()
    for path in ["/../../etc/passwd", "/%2e%2e/%2e%2e/etc/passwd",
                 "/login/../admin", "/" + "a" * 4000,
                 "/login%00", "/nonexistent-xyz", "//login", "/./login"]:
        code, _ = c.get(path, redirect=False)
        check(f"chemin piège {path[:40]}", is_safe(code), f"HTTP {code}")

    for method in ["DELETE", "PUT", "PATCH"]:
        req = urllib.request.Request(BASE + "/login", method=method,
                                     headers={"User-Agent": "crash"})
        try:
            code: Any = urllib.request.build_opener(
                urllib.request.HTTPSHandler(context=_CTX)).open(req, timeout=10).getcode()
        except urllib.error.HTTPError as exc:
            code = exc.code
        except Exception:
            code = -1
        check(f"méthode {method} sur /login", code == -1 or is_safe(code), f"HTTP {code}")

    code, _ = c.get("/login?" + "&".join(f"p{i}=1" for i in range(2000)), redirect=False)
    check("query 2000 paramètres", is_safe(code), f"HTTP {code}")
    code, _ = c.get("/sequence?page=abc&page=-1&page=999999999", redirect=False)
    check("params dupliqués/forgés", is_safe(code), f"HTTP {code}")


# ── 6. Concurrence : pic « classe entière au login » ─────────────────────────

def suite_concurrence(threads: int = 30, total: int = 200) -> None:
    """Rafale parallèle mêlant chemins valides et forgés.

    Reproduit le pic d'usage réel : une classe entière qui se connecte d'un coup.
    C'est cette suite qui a mis au jour l'épuisement du pool MariaDB (retour 023).
    Sous un pool correctement dimensionné (`DB_POOL_SIZE`), on attend 0 réponse 5xx.
    """
    print(f"\n== 6. Concurrence ({threads} threads, {total} requêtes) ==")
    paths = ["/login", "/sequence/show/999999", "/conception/scenario/abc",
             "/nonexistent", "/classe/show/-1", "/", "/ma-sequence"]

    def hit(i: int) -> Any:
        path = paths[i % len(paths)]
        req = urllib.request.Request(BASE + path, headers={"User-Agent": "burst"})
        try:
            return urllib.request.build_opener(
                urllib.request.HTTPSHandler(context=_CTX)).open(req, timeout=15).getcode()
        except urllib.error.HTTPError as exc:
            return exc.code
        except Exception as exc:
            return f"ERR:{type(exc).__name__}"

    with cf.ThreadPoolExecutor(max_workers=threads) as ex:
        res = list(ex.map(hit, range(total)))
    dist = dict(Counter(res))
    cinq = sum(1 for c in res if isinstance(c, int) and c >= 500)
    erreurs = sum(1 for c in res if isinstance(c, str))
    print(f"  distribution : {dist}")
    check("aucune erreur serveur (5xx) sous charge", cinq == 0, f"{cinq} réponses 5xx")
    check("aucune erreur de connexion", erreurs == 0, f"{erreurs} erreurs socket")


def main() -> int:
    global BASE
    parser = argparse.ArgumentParser(description="Crash tests HTTP de RéférenCiel Manager")
    parser.add_argument("--base", default=BASE, help="URL de base (défaut : %(default)s)")
    parser.add_argument("--threads", type=int, default=30, help="Threads de la rafale (suite 6)")
    parser.add_argument("--total", type=int, default=200, help="Requêtes de la rafale (suite 6)")
    args = parser.parse_args()
    BASE = args.base

    print("=== CRASH TESTS — RéférenCiel Manager ===")
    print(f"Cible : {BASE}")
    suite_auth()
    suite_acces()
    suite_ids("admin")
    suite_post_forges("admin")
    suite_http()
    suite_concurrence(args.threads, args.total)

    print(f"\n=== RÉSULTAT : {_ok} OK, {len(_ko)} KO ===")
    for k in _ko:
        print(f"  KO: {k}")
    return 1 if _ko else 0


if __name__ == "__main__":
    sys.exit(main())
