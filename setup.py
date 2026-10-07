"""Prepara /config antes de arrancar Home Assistant.

Lo ejecuta el entrypoint de docker-compose.yml en cada arranque del contenedor.
Todas las tareas son idempotentes: si ya estan hechas, no cambian nada.
"""
import io
import json
import os
import shutil
import urllib.request
import zipfile

CONFIG = os.environ.get("HA_CONFIG_DIR", "/config")
CONF_YAML = os.path.join(CONFIG, "configuration.yaml")
HERE = os.path.dirname(os.path.abspath(__file__))

HACS_VERSION = "2.0.5"
TRUSTED_PROXIES = ["172.16.0.0/12", "10.0.0.0/8", "192.168.0.0/16"]


def read_conf():
    with open(CONF_YAML) as f:
        return f.read()


def ensure_configuration_yaml():
    if not os.path.exists(CONF_YAML):
        with open(CONF_YAML, "w") as f:
            f.write("default_config:\n")
        print("[setup] configuration.yaml creado")


def remove_http_block():
    """Desde HA 2026.9 la config HTTP vive en .storage/http; el bloque http: del YAML se ignora."""
    lines = read_conf().splitlines(True)
    out, skip = [], False
    for line in lines:
        if line.startswith("http:"):
            skip = True
            continue
        if skip and (line.startswith((" ", "\t")) or not line.strip()):
            continue
        skip = False
        out.append(line)
    if len(out) != len(lines):
        with open(CONF_YAML, "w") as f:
            f.write("".join(out).rstrip() + "\n")
        print("[setup] Bloque http: eliminado de configuration.yaml")


def ensure_themes():
    os.makedirs(os.path.join(CONFIG, "themes"), exist_ok=True)
    if "frontend:" not in read_conf():
        with open(CONF_YAML, "a") as f:
            f.write("\nfrontend:\n  themes: !include_dir_merge_named themes\n")
        print("[setup] Carga de temas activada")


def ensure_editor_includes():
    """Necesario para que el editor visual guarde automatizaciones, scripts y escenas."""
    for key, fname, empty in [("automation", "automations.yaml", "[]\n"),
                              ("script", "scripts.yaml", ""),
                              ("scene", "scenes.yaml", "[]\n")]:
        path = os.path.join(CONFIG, fname)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(empty)
        if not any(line.startswith(key + ":") for line in read_conf().splitlines()):
            with open(CONF_YAML, "a") as f:
                f.write(key + ": !include " + fname + "\n")
            print("[setup] " + key + " activado")


def ensure_proxy():
    """Asegura que la config HTTP estable acepte a Traefik como proxy."""
    path = os.path.join(CONFIG, ".storage", "http")
    if not os.path.exists(path):
        print("[setup] .storage/http no existe todavia")
        return
    with open(path) as f:
        doc = json.load(f)
    stable = doc.get("data", doc).setdefault("stable", {})
    if stable.get("use_x_forwarded_for"):
        return
    stable["use_x_forwarded_for"] = True
    stable["trusted_proxies"] = TRUSTED_PROXIES
    with open(path, "w") as f:
        json.dump(doc, f, indent=4)
    print("[setup] Proxy de Traefik configurado en .storage/http")


def ensure_hacs():
    target = os.path.join(CONFIG, "custom_components", "hacs")
    if os.path.isdir(target):
        return
    url = "https://github.com/hacs/integration/releases/download/" + HACS_VERSION + "/hacs.zip"
    try:
        data = urllib.request.urlopen(url, timeout=60).read()
        os.makedirs(target)
        zipfile.ZipFile(io.BytesIO(data)).extractall(target)
        print("[setup] HACS " + HACS_VERSION + " instalado")
    except Exception as e:
        print("[setup] No se pudo instalar HACS: " + str(e))


def install_panel():
    src = os.path.join(HERE, "panel.html")
    if not os.path.exists(src):
        print("[setup] panel.html no disponible")
        return
    www = os.path.join(CONFIG, "www")
    os.makedirs(www, exist_ok=True)
    shutil.copyfile(src, os.path.join(www, "panel.html"))
    print("[setup] Panel instalado en /local/panel.html")


def main():
    ensure_configuration_yaml()
    remove_http_block()
    ensure_themes()
    ensure_editor_includes()
    ensure_proxy()
    ensure_hacs()
    install_panel()


if __name__ == "__main__":
    main()
