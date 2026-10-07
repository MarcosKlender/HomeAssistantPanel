# HomeAssistantPanel

Configuración de Home Assistant (Docker + Traefik) y un panel ligero para tablets antiguas (pensado para Safari 10 / iPad 4).

## Qué hay aquí

| Archivo | Qué hace |
|---|---|
| `docker-compose.yml` | Home Assistant detrás de Traefik. Al arrancar descarga `setup.py` y `panel/panel.html` de este repo, **fijados a un commit** (`PANEL_REF`), y ejecuta `setup.py`. |
| `setup.py` | Prepara `/config`: proxy de Traefik en `.storage/http`, quita el bloque `http:` obsoleto, activa temas y el editor de automatizaciones, instala HACS (versión fija) y copia el panel a `/config/www`. Idempotente. |
| `panel/panel.html` | Panel en ES5 puro. Pestañas por piso y tarjetas agrupadas por área según la configuración de Home Assistant. Luces, puertas y aspiradora. |
| `.env.example` | Plantilla de variables. Los valores reales van en el editor de entorno de Hostinger, nunca en el repo. |

## Variables (`.env` en Hostinger)

| Variable | Ejemplo |
|---|---|
| `TRAEFIK_HOST` | `home.ejemplo.com` |
| `TZ` | `America/Guayaquil` |
| `PANEL_REPO` | `MarcosKlender/HomeAssistantPanel` |
| `PANEL_REF` | hash completo del commit (40 caracteres) |

## Actualizar

1. Cambia lo que necesites, haz commit y push.
2. Copia el hash del commit (`git rev-parse HEAD`) en `PANEL_REF` en Hostinger.
3. Reinicia el contenedor.

Si GitHub no responde al arrancar, se usa la última copia guardada en `/config/.panel`.

## Panel

- URL: `https://<TRAEFIK_HOST>/local/panel.html`
- Necesita un token de acceso de larga duración de un usuario **sin permisos de administrador**. El token se pega en el dispositivo y se guarda solo en su `localStorage`; también se puede pasar una vez con `panel.html#token=...` (el hash no se envía al servidor y el panel lo borra de la URL).
- Se ocultan las entidades marcadas como ocultas en Home Assistant (por ejemplo, los `switch` convertidos en luces).

## Seguridad

- Este repo no contiene secretos. **Nunca** subas tokens, contraseñas ni `.env`.
- `PANEL_REF` fija un commit concreto: ningún cambio en GitHub llega al servidor hasta que actualices el hash.
- `panel.html` se sirve desde el mismo dominio que Home Assistant, así que revisa cualquier cambio antes de fijarlo.
