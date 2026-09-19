.extern led_islem

_start:
    addi x7, x0, 3      # Döngü sayacı: LED 3 kez yanıp sönecek
    
ana_dongu:
    jal x1, led_islem   # Fonksiyonu çağır (Dönüş adresi x1'e kaydedilir)
    
    addi x7, x7, -1     # Ana sayacı azalt
    bne x7, x0, ana_dongu # Eğer 3 kez olmadıysa tekrarla
    
bitis:
    jal x0, bitis       # Program bitti, sonsuz döngüde bekle