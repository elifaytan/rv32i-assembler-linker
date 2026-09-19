# RV32I Two-Pass Assembler

RV32I komut kümesinin belirli bir bölümünü destekleyen, Python ile geliştirilmiş iki geçişli (Two-Pass) assembler projesidir.

Proje; assembly kaynak kodunu okuyarak etiketleri ve adresleri belirler, komutları RV32I makine koduna dönüştürür ve sonuçları binary ve hexadecimal formatlarda üretir.

Assembler içerisinde Opcode Table ve Symbol Table veri yapıları bağlı liste (Linked List) mantığı kullanılarak oluşturulmuştur.

## Özellikler

- Two-Pass Assembler mimarisi
- RV32I komutlarının makine koduna dönüştürülmesi
- Symbol Table oluşturulması
- Opcode Table oluşturulması
- Symbol ve Opcode tablolarında bağlı liste kullanımı
- Label tanımlama ve adres çözümleme
- Register kontrolü
- Immediate değerlerin işlenmesi
- Two's Complement dönüşümü
- Branch offset hesaplama
- Assembly direktiflerinin işlenmesi
- Binary makine kodu üretimi
- Hexadecimal makine kodu üretimi
- Adres bilgilerinin hesaplanması
- Hatalı register ve operand kontrolleri
- Yorum satırlarının temizlenmesi

## Desteklenen Komut Formatları

Projede RV32I mimarisindeki aşağıdaki komut formatları desteklenmektedir:

### R-Type

Desteklenen komutlar:

- `add`
- `sub`
- `and`
- `or`
- `xor`
- `sll`
- `srl`

R-Type komutlarında `rd`, `rs1` ve `rs2` register alanları ile `funct3`, `funct7` ve opcode değerleri kullanılarak 32 bit makine kodu oluşturulur.

### I-Type

Desteklenen komutlar:

- `addi`
- `lw`
- `jalr`

Immediate değerler 12 bit olarak işlenir ve gerekli durumlarda Two's Complement yöntemi kullanılır.

### S-Type

Desteklenen komut:

- `sw`

Store işlemlerinde immediate değeri uygun bit alanlarına ayrılarak RV32I S-Type formatında kodlanır.

### B-Type

Desteklenen komutlar:

- `beq`
- `bne`

Branch komutlarında hedef label ile mevcut program counter arasındaki fark hesaplanarak branch offset değeri oluşturulur.

## Desteklenen Assembly Direktifleri

Assembler aşağıdaki direktifleri desteklemektedir:

- `.text`
- `.data`
- `.word`
- `.byte`
- `.org`
- `.end`

### `.text`

Kod bölümüne geçiş yapmak için kullanılır.

### `.data`

Veri bölümüne geçiş yapmak için kullanılır.

### `.word`

32 bit veri tanımlamak için kullanılır.

### `.byte`

8 bit veri tanımlamak için kullanılır.

### `.org`

Programın başlangıç adresini veya mevcut adresi belirlemek için kullanılır.

### `.end`

Assembly kaynak kodunun sonunu belirtir.

## Two-Pass Assembler Çalışma Mantığı

Assembler iki temel geçiş kullanarak çalışmaktadır.

### Pass 1

İlk geçişte kaynak assembly kodu satır satır incelenir.

Bu aşamada:

- Label tanımları bulunur.
- Her label için adres hesaplanır.
- Symbol Table oluşturulur.
- Komut ve direktiflerin bellek üzerinde kaplayacağı alan hesaplanır.

Örneğin:

    start: add x1, x2, x3

satırındaki `start` etiketi bulunduğu adres ile Symbol Table içerisine eklenir.

### Pass 2

İkinci geçişte komutlar gerçek makine koduna dönüştürülür.

Bu aşamada:

- Opcode Table üzerinden komut bilgileri alınır.
- Register değerleri binary formata dönüştürülür.
- Immediate değerler işlenir.
- Branch komutları için Symbol Table kullanılır.
- 32 bit binary makine kodları oluşturulur.
- Binary değerlerin hexadecimal karşılıkları hesaplanır.
- Sonuçlar çıktı dosyasına yazılır.

## Opcode Table

Opcode Table, desteklenen RV32I komutlarının özelliklerini saklamak için kullanılmaktadır.

Her kayıt aşağıdaki bilgileri içerebilir:

- Mnemonic
- Instruction Format
- Opcode
- funct3
- funct7

Opcode Table bağlı liste veri yapısı kullanılarak geliştirilmiştir.

Her opcode kaydı bir sonraki kaydı gösteren bir işaretçi içermektedir.

## Symbol Table

Symbol Table assembly kodunda bulunan label ve adres bilgilerini saklamaktadır.

Örnek:

    start -> 0x00000000
    val1  -> 0x0000001C
    val2  -> 0x00000020
    end   -> 0x00000024

Symbol Table da bağlı liste tabanlı olarak geliştirilmiştir.

Assembler branch komutlarını işlerken hedef label adreslerini bu tablodan bulmaktadır.

## Örnek Assembly Kodu

Projede kullanılan örnek assembly kodu aşağıdaki yapıdadır:

    .org 0x0000
    .text

    start:  add x1, x2, x3
            sub x4, x1, x5
            addi x6, x0, 10
            lw x7, 0(x1)
            sw x7, 4(x1)
            beq x1, x2, end
            bne x1, x3, start

    .data
    val1:   .word 25
    val2:   .byte 7

    .text
    end:    or x8, x1, x2
            .end

## Örnek Çıktı

Assembler her komut için adres, komut türü, kaynak kod, binary makine kodu ve hexadecimal karşılığını oluşturur.

Örnek:

    ADDRESS  | TYPE        | SOURCE
    00000000 | INSTRUCTION | add x1, x2, x3
    00000004 | INSTRUCTION | sub x4, x1, x5
    00000008 | INSTRUCTION | addi x6, x0, 10

Örneğin:

    add x1, x2, x3

komutu için oluşturulan hexadecimal makine kodu:

    0x003100B3

şeklindedir.

Projede oluşturulan örnek çıktı dosyasında bütün komutların binary ve hexadecimal karşılıkları görüntülenebilir.

## Hata Kontrolleri

Assembler içerisinde çeşitli temel hata kontrolleri bulunmaktadır.

Bunlardan bazıları:

- Geçersiz register kontrolü
- Register aralığının kontrol edilmesi
- Hatalı operand sayısı
- Geçersiz bellek operandı
- Yinelenen label kontrolü
- Geçersiz label adı
- Desteklenmeyen komut kontrolü

RV32I register değerleri `x0` ile `x31` arasında kontrol edilmektedir.

## Kullanılan Teknolojiler

- Python
- Jupyter Notebook
- RISC-V
- RV32I Instruction Set
- Assembly Language
- Linked List
- Symbol Table
- Opcode Table
- Two-Pass Assembler
- Binary Encoding
- Hexadecimal Encoding

## Proje Dosyaları

- `sistem_programlama_kod (1).ipynb` — Two-Pass RV32I assembler kodlarının bulunduğu Jupyter Notebook
- `output (1).txt` — Assembler tarafından üretilen örnek çıktı
- `README.md` — Proje açıklamaları

## Çalıştırma

Jupyter Notebook dosyasını açarak hücreleri sırasıyla çalıştırın.

Notebook içerisinde örnek assembly kaynak kodundan `input.asm` dosyası oluşturulur.

Daha sonra assembler:

1. İlk geçişi gerçekleştirir.
2. Symbol Table oluşturur.
3. İkinci geçişi gerçekleştirir.
4. RV32I komutlarını makine koduna dönüştürür.
5. Sonuçları `output.txt` dosyasına yazar.
6. Opcode Table ve Symbol Table bilgilerini görüntüler.

## Projenin Amacı

Bu projenin amacı assembler çalışma mantığının uygulamalı olarak öğrenilmesi ve assembly komutlarının makine koduna nasıl dönüştürüldüğünün incelenmesidir.

Two-Pass yöntemi kullanılarak label adreslerinin çözülmesi, Symbol Table ve Opcode Table oluşturulması, farklı RV32I komut formatlarının kodlanması ve binary/hexadecimal makine kodlarının üretilmesi gerçekleştirilmiştir.

Proje aynı zamanda bağlı liste tabanlı veri yapılarının sistem programlama problemlerinde nasıl kullanılabileceğini göstermektedir.

## Proje Notu

Bu proje Sistem Programlama dersi kapsamında geliştirilmiş akademik bir çalışmadır.
