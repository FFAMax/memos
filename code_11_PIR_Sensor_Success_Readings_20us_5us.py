import board
import time
import digitalio
import microcontroller
import gc # Импортируем сборщик мусора
import adafruit_pioasm
import rp2pio
import array
import struct

delay_us = microcontroller.delay_us


# Ассемблерная вставка для PIO (Частота 1 МГц, 1 такт = 1 мкс)
pio_script = """
.program custom_reader
.wrap_target
start:
;    set pindirs, 1
;    set pins, 1
;    nop [31]
;    set pindirs, 0
;    nop [31]
;    nop [31]
;    set pins, 0
;    nop [31]
;    set pindirs, 0
;    wait 0 pin 0

    ; Preamble 
    ; ==========================================
    ; 2. Выставляем HIGH на 8 такта, затем High-Z
    ; ==========================================
;    set pindirs, 1       ; Включаем на выход (1 такт)
;    set pins, 1          ; Ставим в 1 (1 такт)
;    nop [5]              ; Ждем еще 2 такта (итого 4 такта HIGH)
;    set pindirs, 0       ; Переводим в High-Z (вход)

    ; Ждем, пока линия физически не поднимется в HIGH
;wait_high:
;    jmp pin, high_start
;    jmp wait_high

    ; ==========================================
    ; 3. Проверяем, что сигнал HIGH держится 300 мкс
    ; ==========================================
high_start:
;    set x, 9             ; Внешний цикл на 10 итераций
;outer_300:
;    set y, 13            ; Внутренний цикл на 14 итераций
;inner_300:
;    jmp pin, is_high_ok  ; Если HIGH - продолжаем нормально
;    jmp start            ; Если упало в LOW (0) - СБРОС в начало!
;is_high_ok:
;    jmp y--, inner_300
;    jmp x--, outer_300   ; Математика: 10 * (1 + 14*2 + 1) = 300 тактов = 300 мкс.

    ; ==========================================
    ; 4. Условия выполнены! Записываем первый бит (1)
    ; ==========================================
    ;set y, 1
    ;in y, 1              ; Сдвигаем '1' в регистр данных (ISR)

    ; ==========================================
    ; 5. Тактируем 19 раз (чтение 19 бит)
    ; ==========================================
    set x, 18            ; Счетчик цикла от 18 до 0 (19 итераций)
clock_loop:
    ; Перевод линии в 0 на 4 такта
    set pins, 0          
    set pindirs, 1       
    nop [1]

    ; Перевод линии в 1 и сразу в High-Z
    set pins, 1
    nop [1]
    set pindirs, 0       

    ; Пропуск 20 us
    nop [11]             ; Инструкция(1) + задержка(18) + in_pins(1) = 20 тактов

    ; Чтение значения пина и сохранение
    in pins, 1           ; Читаем 1 бит физического состояния в ISR

    jmp x--, clock_loop  ; Повторяем 19 раз

    ; Отправляем собранные 20 бит в Python
    push block           
.wrap
"""

pio_script2 = """
.program custom_reader2
.wrap_target
start:
    set pindirs, 0
wait_high:
    jmp pin, high_start
    jmp wait_high

    ; ==========================================
    ; 3. Проверяем, что сигнал HIGH держится 300 мкс
    ; ==========================================
high_start:
    set x, 9             ; Внешний цикл на 10 итераций
outer_300:
    set y, 13            ; Внутренний цикл на 14 итераций
inner_300:
    jmp pin, is_high_ok  ; Если HIGH - продолжаем нормально
    jmp start            ; Если упало в LOW (0) - СБРОС в начало!
is_high_ok:
    jmp y--, inner_300
    jmp x--, outer_300   ; Математика: 10 * (1 + 14*2 + 1) = 300 тактов = 300 мкс.

    ; ==========================================
    ; 4. Условия выполнены! Записываем первый бит (1)
    ; ==========================================
    set y, 1
    in y, 1              ; Сдвигаем '1' в регистр данных (ISR)

    ; ==========================================
    ; 5. Тактируем 19 раз (чтение 19 бит)
    ; ==========================================
    set x, 18            ; Счетчик цикла от 18 до 0 (19 итераций)
clock_loop:
    ; Перевод линии в 0 на 4 такта
    set pins, 0          
    set pindirs, 1       
    nop [3]

    ; Перевод линии в 1 и сразу в High-Z
    set pins, 1
    nop [1]
    set pindirs, 0       

    ; Пропуск 20 us
    nop [11]             ; Инструкция(1) + задержка(18) + in_pins(1) = 20 тактов
    ; 11 - 20us - measured

    ; Чтение значения пина и сохранение
    in pins, 1           ; Читаем 1 бит физического состояния в ISR

    jmp x--, clock_loop  ; Повторяем 19 раз

    ; Отправляем собранные 20 бит в Python
    push block           
.wrap
"""

# Компилируем ассемблерный код
assembled = adafruit_pioasm.assemble(pio_script)
assembled2 = adafruit_pioasm.assemble(pio_script2)
pir_pin_asm = board.GP19

#pir_pin = digitalio.DigitalInOut(board.GP19)
#pir_pin.direction = digitalio.Direction.OUTPUT
#pir_pin.value = False
#pir_pin.direction = digitalio.Direction.INPUT
#pir_pin.deinit()

# 1. Питание (GP20) - НЕ ТРОГАЕМ, РАБОТАЕТ КАК И БЫЛО
pin_gp20 = digitalio.DigitalInOut(board.GP20)
pin_gp20.direction = digitalio.Direction.OUTPUT
pin_gp20.value = True 
#print("Питание подано. Прогрев 3 секунды...")
#delay_us(600) # Let sensor boot up
#time.sleep(1)

#if not pir_pin.value:
#    pir_pin.direction = digitalio.Direction.OUTPUT
    #pir_pin.value = True
#    delay_us(100)
#pir_pin.direction = digitalio.Direction.INPUT
#pir_pin.pull = digitalio.Pull.UP
#delay_us(10000)
#pir_pin.deinit()

#pir_pin.deinit()
#time.sleep(1000)
#pir_pin.switch_to_input()
#delay_us(500)
#pir_pin.deinit()
#delay_us(10000) # Let sensor see changes

#print("\n\nReady!\n\n")
#time.sleep(1)
# Создаем стейт-машину
sm = rp2pio.StateMachine(
    assembled,
    frequency=1_000_000,           # 1 МГц = 1 мкс
    first_set_pin=pir_pin_asm,     # Для инструкций 'set pins, X'
    first_in_pin=pir_pin_asm,      # Для инструкций 'in pins, 1'
    jmp_pin=pir_pin_asm,           # Для инструкций 'jmp pin, ...'
    set_pin_count=1,
    in_pin_count=1,
    in_shift_right=False,          # Сдвиг влево, чтобы 1-й бит был старшим
    push_threshold=20                 # Можем указать, но делаем push вручную
)
#pin_gp20.value = False
#print("Ожидание данных от датчика...")

# Массив для получения 32-битного слова из PIO
data = array.array('I', [0])
# Эта функция заблокирует Python, пока PIO не пройдет весь цикл проверок
# и не соберет 20 бит без ошибок. 
sm.readinto(data)
sm.deinit()
# Получаем 32-битное число. Наши 20 бит находятся в младшей части
val = data[0]

# Формируем строку из 20 бит
# (Мы сдвигали влево, поэтому данные лежат в формате: БИТ0 БИТ1 ... БИТ19)
bits = [(val >> i) & 1 for i in range(19, -1, -1)]
ffbits_str = "".join(map(str, bits))
print(f"Получено: {ffbits_str}")

while True:
    sm = rp2pio.StateMachine(
        assembled2,
        frequency=1_000_000,           # 1 МГц = 1 мкс
        first_set_pin=pir_pin_asm,     # Для инструкций 'set pins, X'
        first_in_pin=pir_pin_asm,      # Для инструкций 'in pins, 1'
        jmp_pin=pir_pin_asm,           # Для инструкций 'jmp pin, ...'
        set_pin_count=1,
        in_pin_count=1,
        in_shift_right=False,          # Сдвиг влево, чтобы 1-й бит был старшим
        push_threshold=20                 # Можем указать, но делаем push вручную
    )
            
    sm.readinto(data)
    sm.deinit()
    val = data[0]
    bits = [(val >> i) & 1 for i in range(19, -1, -1)]
    ffbits_str = "".join(map(str, bits))
    # 2. Отбрасываем первые два и последний бит, оставляя 16 бит
    # Сдвиг вправо на 1 убирает последний бит, а маска & 0xFFFF оставляет только 16 бит
    val_16bit = (val >> 1) & 0xFFFF

    # 2. Декодируем как SIGNED INT16 (символ 'h' вместо 'e')
    # Используем '<h' (Little Endian) или '>h' (Big Endian) в зависимости от датчика
    # Для проверки возьмем '>h'
    raw_bytes = struct.pack('>H', val_16bit)
    pir_signal = struct.unpack('>h', raw_bytes)[0]

    #print(f"Результат float: {float_val}")
    print(f"Получено: {ffbits_str} {pir_signal}")
    pir_pin = digitalio.DigitalInOut(board.GP19)
    pir_pin.direction = digitalio.Direction.OUTPUT
    pir_pin.value = False
    pir_pin.deinit()

#pir_pin = digitalio.DigitalInOut(board.GP19)
#pir_pin.direction = digitalio.Direction.INPUT

time.sleep(1000)


# --- БЛОК ОПТИМИЗАЦИИ ---
# Локальные переменные работают быстрее, чем глобальные атрибуты.
# Кэшируем объекты, чтобы Python не тратил время на их поиск в цикле.
DIR_OUT = digitalio.Direction.OUTPUT
DIR_IN = digitalio.Direction.INPUT

# Заранее выделяем память под массив! Никаких .append() в быстром цикле.


i=20 #stopped at 333
j=0
while True:
    # Отключаем сборщик мусора на время критичного к таймингам цикла
    gc.disable()
    
    bits = [0] * i

    #bits = [] 
    pir_pin.direction = DIR_OUT
    pir_pin.value = True # First pulse
    
    pir_pin.direction = DIR_IN
    #pir_pin.pull = digitalio.Pull.DOWN
    delay_us(500)

    pir_pin.direction = DIR_OUT
    pir_pin.value = False
    delay_us(5)
    pir_pin.direction = DIR_IN
    for bit in range (19):
        pir_pin.direction = DIR_OUT
        pir_pin.value = True
        pir_pin.direction = DIR_IN
        delay_us(1)
        pir_pin.direction = DIR_OUT
        pir_pin.value = False
    pir_pin.direction = DIR_IN
    
    # After ~ 200us peer should pull to HI, monitoring for HI
    #k = 0
    while pir_pin.value == 0:
        #k=k+1
        #delay_us(1)
        pass
    #print(f"Log HI. Exit after {k} cycles")
    delay_us(2500) # Okay we see HI but will keep for some time - peer not expecting quick reaction
    
#Responding on "Hello" HI
    pir_pin.direction = DIR_OUT
    pir_pin.value = False
    pir_pin.direction = DIR_IN
    #while pir_pin.value == 0:
    #   pass 
    delay_us(400)
    
# Peer set LOW
    pir_pin.direction = DIR_OUT # 1 tick
    pir_pin.value = True
    delay_us(10)
    pir_pin.direction = DIR_IN
    delay_us(400)
# Peer should pull to HI and keep HI

    #k=0
    #delay_us(1)
    #while pir_pin.value == 0:
    #    k=k+1
    #    delay_us(1)
    #print(f"Log HI. Exit after {k} cycles")
# Okay we saw peer's HI - peer ready
    
    #pir_pin.direction = DIR_OUT
    #pir_pin.value = False # Interrupt peer's HI

    # Next 19 cycles with high-Z
    for bit in range (19): # Reading from sensor
        #pir_pin.direction = DIR_OUT
        #pir_pin.value = True
        pir_pin.direction = DIR_IN
        delay_us(20)
        pir_pin.direction = DIR_OUT
        pir_pin.value = False
        pir_pin.direction = DIR_IN
        delay_us(20)
        
    pir_pin.direction = DIR_IN
    time.sleep(100000)

    for bit in reversed(range (i)): #0-i19
        pir_pin.direction = DIR_OUT
        pir_pin.value = True
        delay_us(1)

        # 1. Если дошли до битов режима работы [8:7], управляем значением сами
        if bit == 8:
            bit_to_send = 0  # Для Interrupt Readout (бинарное 01: 8-й бит = 0)
            pir_pin.value = False
            delay_us(50)
        elif bit == 7:
            bit_to_send = 1  # Для Interrupt Readout (бинарное 01: 7-й бит = 1)
            pir_pin.value = True
            delay_us(50)
        else:
            pir_pin.value = True
            delay_us(50)

        pir_pin.direction = DIR_OUT
        pir_pin.value = False
        delay_us(5)
    time.sleep(3)
    pir_pin.direction = DIR_OUT
    pir_pin.value = True # First pulse
    
    pir_pin.direction = DIR_IN
    #pir_pin.pull = digitalio.Pull.DOWN
    delay_us(150)

    pir_pin.direction = DIR_OUT
    pir_pin.value = False
    delay_us(5)
    for bit in reversed(range (i)): #0-i19
        pir_pin.direction = DIR_OUT
        pir_pin.value = True
        delay_us(1)

        pir_pin.direction = DIR_IN
        delay_us(20)
        bits[bit] = (1 if pir_pin.value else 0)

        pir_pin.direction = DIR_OUT
        pir_pin.value = False
        delay_us(5)
    # Включаем сборщик мусора обратно
    gc.enable()



    ffbits_str = "".join(map(str, bits))
    if j == 10:
        j=0
        i=i+1
        pin_gp20.value = False
        time.sleep(5) 

        pin_gp20.value = True
        time.sleep(1)

    else:
        j=j+1
    print(f"{ffbits_str} i={i}")
    #pir_pin.direction = DIR_OUT
    pir_pin.direction = DIR_OUT
    pir_pin.value = False
    delay_us(5)

    pir_pin.direction = DIR_IN
    time.sleep(10000) 

