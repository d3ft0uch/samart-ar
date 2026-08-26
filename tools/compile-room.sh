#!/bin/bash
# Компиляция image-таргетов для room.html через локальный HTTP + браузер.
# Использование:
#   tools/compile-room.sh images/img1.JPG images/img2.JPG images/img3.JPG images/img4.JPG
# Порядок картинок = порядок ROOM_CONFIG.spots в works.js.
#
# Что делает:
#  1. Поднимает python http.server на 8765 (в фоне).
#  2. Открывает tools/compile-room.html?auto=... в дефолтном браузере.
#  3. Ждёт, пока браузер скачает room.mind в ~/Downloads/.
#  4. Переносит в targets/room.mind.
#  5. Гасит сервер.
#
# Требования: python3, дефолтный браузер (macOS: open), запись в ~/Downloads.

set -e
cd "$(dirname "$0")/.."

if [ "$#" -lt 1 ]; then
  echo "usage: $0 image1 [image2 ...] (пути от корня репозитория)" >&2
  exit 1
fi

# Проверяем, что все файлы существуют
for p in "$@"; do
  [ -f "$p" ] || { echo "не найден: $p" >&2; exit 1; }
done

# Формируем auto-параметр (относительный путь от tools/compile-room.html)
auto=""
for p in "$@"; do
  auto="${auto},../${p}"
done
auto="${auto:1}"  # убираем ведущую запятую

PORT=8765
DL="$HOME/Downloads/room.mind"
DEST="targets/room.mind"

rm -f "$DL"
mkdir -p targets

python3 -m http.server $PORT > /tmp/samart-http.log 2>&1 &
SERVER_PID=$!
trap "kill $SERVER_PID 2>/dev/null; wait 2>/dev/null; true" EXIT

sleep 1
URL="http://127.0.0.1:${PORT}/tools/compile-room.html?auto=${auto}"
echo "открываю: $URL"

if command -v open >/dev/null 2>&1; then
  open "$URL"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL"
else
  echo "открой в браузере вручную: $URL"
fi

echo "жду ~/Downloads/room.mind (до 120 сек)…"
for i in $(seq 1 120); do
  if [ -f "$DL" ]; then
    mv "$DL" "$DEST"
    ls -la "$DEST"
    echo "готово: $DEST"
    exit 0
  fi
  sleep 1
done

echo "не дождался room.mind. Проверь окно браузера — возможно, скачивание нужно подтвердить вручную." >&2
exit 2
