#!/bin/bash
# apt install imagemagick
# Задайте таймкод (например, 00:01:30 — 1 минута 30 секунд)
TIMECODE="00:01:30"

for file in *.mp4; do
    # Берем имя файла без расширения
    name="${file%.*}"
    # Извлекаем 1 точный кадр без потери качества в PNG
    ffmpeg -y -ss "$TIMECODE" -i "$file" -vframes 1 -q:v 1 "${name}.png"
done
convert *.png -crop 1920x100+0+540 +repage -append result_stripes.png


