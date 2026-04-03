# PubliAlert — Instrucciones de instalación

## Archivos incluidos
- `index.html` — App principal
- `sw.js` — Service Worker (necesario para PWA)
- `manifest.json` — Manifiesto PWA (necesario para "Añadir a inicio")
- `icon-192.png` — Icono app 192×192
- `icon-512.png` — Icono app 512×512

---

## Cómo subir a GitHub Pages (gratis, HTTPS automático)

### Paso 1 — Crea cuenta en GitHub
Ve a https://github.com y regístrate (gratis).

### Paso 2 — Crea un repositorio nuevo
1. Pulsa el botón verde **"New"** o ve a https://github.com/new
2. Nombre del repositorio: `publialert` (o el que quieras)
3. Marca **"Public"**
4. Pulsa **"Create repository"**

### Paso 3 — Sube los archivos
En la página del repositorio vacío:
1. Pulsa **"uploading an existing file"**
2. Arrastra y suelta los 5 archivos: `index.html`, `sw.js`, `manifest.json`, `icon-192.png`, `icon-512.png`
3. Pulsa **"Commit changes"**

### Paso 4 — Activa GitHub Pages
1. Ve a **Settings** (pestaña del repositorio)
2. En el menú izquierdo busca **"Pages"**
3. En "Branch" selecciona **main** y carpeta **/ (root)**
4. Pulsa **"Save"**

### Paso 5 — Tu URL
En 1-2 minutos estará disponible en:
```
https://TU_USUARIO.github.io/publialert/
```

---

## Instalar como app en el móvil

### Android (Chrome)
Abre la URL en Chrome → aparecerá un banner **"Instalar PubliAlert"** → pulsa Instalar.

### iPhone / iPad (Safari)
1. Abre la URL en **Safari** (no Chrome en iOS)
2. Pulsa el botón **Compartir** (□↑) en la barra inferior
3. Desplázate y toca **"Añadir a pantalla de inicio"**
4. Pulsa **"Añadir"**

La app aparecerá en tu pantalla de inicio como una app nativa, sin barra del navegador.

---

## Activar notificaciones
Al abrir la app aparecerá un banner amarillo para activar notificaciones.
**Actívalas antes de minimizar la app** — así recibirás el aviso aunque estés en otra app.
