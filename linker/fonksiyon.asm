.global led_islem

led_islem:
    # x5 register'ını LED durumu gibi düşünelim
    addi x5, x0, 1      # LED'i yak (x5 = 1)
    
    # Birinci gecikme döngüsü
    addi x6, x0, 50     # Gecikme sayacı (kısa bir test için 50)
bekle1:
    addi x6, x6, -1     # Sayacı azalt
    bne x6, x0, bekle1  # 0 değilse döngüye devam
    
    addi x5, x0, 0      # LED'i söndür (x5 = 0)
    
    # İkinci gecikme döngüsü
    addi x6, x0, 50     
bekle2:
    addi x6, x6, -1
    bne x6, x0, bekle2
    
    jalr x0, x1, 0      # Geri dön (Return)