#!/bin/bash

# Создаем временную папку для полос с текстом
mkdir -p ./temp_stripes

# Шаг 1: Нарезаем полосы и пишем на них текст
for file in *.png; do
    # Пропускаем уже готовые результаты, если они есть
    if [[ "$file" == *"result_"* ]]; then continue; fi

    echo "Обработка: $file"
    
    # 1920x100+0+540 — размер и смещение полосы
    # -gravity NorthWest — разместить текст в верхнем левом углу полосы
    # -pointsize 24 — размер шрифта (можно увеличить, если мелко)
    # -fill white -annotate +15+15 — белый текст со смещением 15px от края
    convert "$file" -crop 1920x100+0+540 +repage \
            -gravity NorthWest -pointsize 24 -fill white \
            -stroke black -strokewidth 1 -annotate +15+15 "%f" \
            "./temp_stripes/strip_$file"
done

# Шаг 2: Склеиваем все оригинальные полосы вертикально
convert ./temp_stripes/strip_*.png -append result_stripes_hq.png

# Удаляем временную папку
rm -rf ./temp_stripes

echo "Готово! Файл сохранен в result_stripes_hq.png"

