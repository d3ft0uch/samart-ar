# WebAR-прототип для выставки

QR → страница → 3D-модель работы → кнопка «Посмотреть в зале (AR)».
Без приложений, без VPN, всё раздаётся как статика.

## Структура

```
samart-ar/
├── index.html      служебная страница: список работ + QR для печати
├── viewer.html     страница посетителя (viewer.html?id=1)
├── works.js        каталог работ: id → модель, название, описание
├── lib/
│   └── model-viewer.min.js   (локальная копия, без CDN)
└── models/
    └── demo.glb    демо-модель — замени на настоящие GLB из Blender
```

## Запуск на localhost

```bash
cd samart-ar
python3 -m http.server 8000
```

Открой http://localhost:8000 — список работ; http://localhost:8000/viewer.html?id=1 — просмотр.

## Проверка с телефона

1. Комп и телефон в одной Wi-Fi-сети.
2. Узнай IP компа (`ip a` / `ipconfig`), открой на телефоне `http://<IP>:8000/viewer.html?id=1`.
3. 3D-просмотр (крутить пальцем) заработает сразу. Кнопка AR по http может
   не появиться — WebXR требует HTTPS. Для полноценного AR-теста с телефона:
   - самый простой путь: залить на любой статик-хостинг с HTTPS
     (GitHub Pages: push в репозиторий → Settings → Pages), или
   - локальный HTTPS: `npx serve --ssl-cert ...` с самоподписанным сертификатом
     (телефон будет ругаться на сертификат — можно принять вручную).

## Добавить работу

1. Экспорт из Blender: File → Export → glTF 2.0, формат **glTF Binary (.glb)**.
2. Если файл больше ~5–10 МБ:
   `npx @gltf-transform/cli optimize work2.glb work2_opt.glb --texture-compress webp`
3. Положи в `models/`, добавь запись в `works.js`.
4. QR для печати появится сам на index.html.

## iOS Quick Look (по желанию)

На айфонах кнопка AR использует Quick Look, которому нужен `.usdz`.
Без него на iOS остаётся обычный 3D-просмотр — это нормальная деградация.
Если хочется AR и на iOS: Blender умеет экспорт в USD (File → Export →
Universal Scene Description, расширение поставить `.usdz`), либо конвертация
GLB → USDZ через Reality Converter (macOS). Файл кладёшь рядом с GLB и
прописываешь поле `usdz` в `works.js`.

## Продакшн

Любой статик-хостинг с HTTPS. Никакого бэкенда нет, внешних CDN нет —
всё лежит в этой папке (кроме предпросмотра QR на index.html, который
ходит на api.qrserver.com; для печати можно сгенерировать QR любым
офлайн-генератором на те же ссылки).

## Деплой на GitHub Pages

```bash
cd samart-ar
git init
git add -A
git commit -m "webar exhibition"
git branch -M main
git remote add origin git@github.com:ВАШ_ЛОГИН/samart-ar.git
git push -u origin main
```

Затем на GitHub: репозиторий → Settings → Pages → Source: **Deploy from a branch**,
Branch: **main**, папка **/ (root)** → Save. Через минуту-две сайт живой:

- https://ВАШ_ЛОГИН.github.io/samart-ar/ — служебная страница с QR
- https://ВАШ_ЛОГИН.github.io/samart-ar/viewer.html?id=1 — работа

QR на index.html сгенерируются уже под этот адрес — открой её на Pages-домене
и сохраняй коды на печать оттуда.

Обновление контента (новые модели, правки описаний):
`git add -A && git commit -m "..." && git push` — Pages пересоберётся сам.

Нюансы:
- Бесплатный Pages работает только с публичным репозиторием (или GitHub Pro).
- Лимит размера репозитория — мягкий 1 ГБ; отдельный файл до 100 МБ.
  С оптимизированными GLB по 5–10 МБ места хватит на десятки работ.
- HTTPS включён по умолчанию — AR-кнопка и все браузерные API работают сразу.
