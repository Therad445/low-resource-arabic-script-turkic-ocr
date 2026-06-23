# Speaker notes — 10-slide defense deck

## Slide 1 — Framing
30 секунд.

Сразу задаю рамку: это не OCR с картинки и не переводчик. Я рассматриваю слой после распознавания: на вход уже приходит шумный OCR или OCR-like текст, а задача модели — приблизить его к clean reference. Это важно, потому что перед поиском, NER и историческим анализом текст нужно хотя бы частично очистить.

## Slide 2 — Where the problem is
35–40 секунд.

В pipeline есть несколько этапов: скан, OCR/HTR, шумный текст, post-correction, чистый текст и дальнейший анализ. Мой фокус — именно между OCR и анализом. Ошибки OCR ломают поиск, индексацию, извлечение сущностей и любые downstream-задачи.

## Slide 3 — Why the task is hard
45 секунд.

Здесь четыре причины. Во-первых, арабская графика: точки, похожие формы, позиционные варианты. Во-вторых, историческая орфография: нельзя просто всё нормализовать современными правилами. В-третьих, мало готовых датасетов именно под такую постановку. В-четвёртых, CER и WER полезны, но не заменяют ручную проверку. Поэтому я не обещаю полную OCR-систему, а строю узкий воспроизводимый эксперимент.

## Slide 4 — Dataset and pipeline
50 секунд.

Я собрал clean corpus и построил synthetic OCR-like noise. Важно, что split сделан по исходным clean lines: варианты одной и той же строки не попадают одновременно в train и test. Это снижает leakage. На синтетике получилось 6400 train-примеров и по 800 valid/test. Дополнительно после synthetic benchmark я добавил real-OCR sanity check через Tesseract.

## Slide 5 — Methodology
45 секунд.

Сравнение сделано не с одной моделью в вакууме. Есть identity baseline, rule-based normalizer, train-derived char-confusion baseline и ByT5-small 512. Метрики: CER, WER, NoSpaceCER, ExactMatch и line-level behavior. NoSpaceCER добавлен специально, потому что WER может сильно улучшаться из-за пробелов и границ слов, а мне важно проверить и character-level effect.

## Slide 6 — Synthetic results
50 секунд.

На synthetic benchmark ByT5-small показывает лучший результат среди методов. CER улучшается умеренно: с 0.086 до 0.080. WER улучшается заметнее: с 0.519 до 0.369. Rule-based normalizer, наоборот, ухудшает результат. Это важный отрицательный результат: грубая нормализация исторического текста опасна.

## Slide 7 — Line-level behavior
45 секунд.

Одна средняя метрика не показывает всю картину. По CER модель улучшает 682 строки из 800, оставляет 60 без изменений и ухудшает 58. Значит, модель в среднем полезна, но не абсолютно безопасна. Whitespace sanity показывает, что WER gain частично связан с пробелами, но effect не сводится только к whitespace.

## Slide 8 — Qualitative examples
50–60 секунд.

Здесь показываю три типа поведения. В improved-примере модель убирает лишние пробелы и делает строку ближе к reference. В unchanged-примере она почти ничего не меняет: это безопасно, но не исправляет реальные ошибки. В worsened-примере локальная правка может ухудшить CER. Поэтому в работе важен error analysis, а не только итоговая таблица.

## Slide 9 — Real-OCR sanity check
60–70 секунд.

Это главный новый sanity check. Я взял 90 line-level примеров с 8 страниц и прогнал их через Arabic-only Tesseract. Tesseract identity даёт CER 0.4508 и WER 1.0888. Synthetic-trained ByT5 снижает CER до 0.4361 и WER до 0.9660. Из 90 строк 40 улучшились, 33 не изменились, 17 ухудшились. Это означает partial transfer, но NoSpaceCER почти не меняется, поэтому robust real character-level correction ещё не решена.

## Slide 10 — Conclusion
45–60 секунд.

Главный вклад: воспроизводимый pilot benchmark для OCR post-correction арабографичного тюркского исторического текста. Есть synthetic benchmark, baselines, ByT5, error analysis, robustness/fallback и real-OCR sanity check. Но это ещё не готовая OCR-система. Следующий шаг — verified real benchmark, line crops, PAGE XML/hOCR, сравнение OCR engines и real-error-aware synthetic noise.

Финальная фраза:
“Это не OCR-система с картинки, а проверенный слой post-correction и основа для будущего OCR/HTR benchmark.”
