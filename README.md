# RV32I Assembler & Linker

RV32I komut kümesi için Python ile geliştirilmiş bir **Two-Pass Assembler ve Linker** projesidir.

Projenin ilk aşamasında assembly kaynak kodları analiz edilerek sembol ve opcode tabloları oluşturulmakta ve RV32I komutları binary/hexadecimal makine koduna dönüştürülmektedir.

İkinci aşamada ise birden fazla assembly modülü ayrı ayrı nesne dosyalarına dönüştürülmekte, global ve external semboller çözülmekte, relocation işlemleri uygulanmakta ve son makine kodu oluşturulmaktadır.

## Özellikler

- Two-Pass Assembler yapısı
- RV32I komutlarının makine koduna dönüştürülmesi
- Symbol Table oluşturulması
- Opcode Table oluşturulması
- Bağlı liste tabanlı tablo yapıları
- Label ve adres çözümleme
- Register ve operand kontrolleri
- Immediate değerlerin işlenmesi
- Two's Complement dönüşümü
- Binary ve hexadecimal makine kodu üretimi
- Birden fazla assembly modülünün işlenmesi
- `.global` sembol desteği
- `.extern` sembol desteği
- Nesne dosyası oluşturma
- Relocation Table oluşturma
- Global Symbol Table oluşturma
- B-Type relocation
- J-Type relocation
- External sembollerin linker tarafından çözülmesi
- Final hexadecimal makine kodu oluşturulması

## Proje Yapısı

Proje iki temel aşamadan oluşmaktadır.

### 1. Two-Pass Assembler

İlk bölümde assembly kaynak kodu iki geçişli assembler yöntemi ile işlenmektedir.

İlk geçişte semboller ve adresler belirlenirken ikinci geçişte komutlar RV32I makine koduna dönüştürülmektedir.

Ana dosyalar:

- `sistem_programlama_kod (1).ipynb` — Two-Pass Assembler uygulaması
- `output (1).txt` — Assembler tarafından oluşturulan örnek çıktı

### 2. Linker ve Relocation

İkinci bölüm `linker/` klasörü içerisinde bulunmaktadır.

Bu aşamada farklı assembly modülleri ayrı ayrı assemble edilmekte ve oluşturulan nesne dosyaları linker tarafından birleştirilmektedir.

Linker klasöründe bulunan temel dosyalar:

- `linker/kodlar.py` — Assembler ve Linker implementasyonu
- `linker/main.asm` — Ana assembly modülü
- `linker/fonksiyon.asm` — İkinci assembly modülü
- `linker/main_nesne.obj` — Ana modülün nesne dosyası
- `linker/fonk_nesne.obj` — Fonksiyon modülünün nesne dosyası
- `linker/main_symbol.txt` — Ana modül sembol tablosu
- `linker/fonk_symbol.txt` — Fonksiyon modülü sembol tablosu
- `linker/global_symbol.txt` — Linker tarafından oluşturulan global sembol tablosu
- `linker/makine_kodu.hex` — Son hexadecimal makine kodu
- `linker/opcode_tablosu.txt` — Opcode bilgileri

## Two-Pass Assembler

Assembler iki temel geçiş kullanmaktadır.

### Pass 1

İlk geçişte assembly kaynak kodu satır satır analiz edilir.

Bu aşamada:

- Label tanımları bulunur.
- Label adresleri hesaplanır.
- Symbol Table oluşturulur.
- Program Counter değerleri takip edilir.
- Global ve external semboller belirlenir.

Örneğin bir label:

    start: add x1, x2, x3

şeklinde tanımlandığında `start` sembolü bulunduğu adres ile Symbol Table içerisine eklenir.

### Pass 2

İkinci geçişte gerçek makine kodu oluşturulur.

Bu aşamada:

- Opcode Table üzerinden komut bilgileri alınır.
- Register değerleri binary formata dönüştürülür.
- Immediate değerler kodlanır.
- Branch hedefleri hesaplanır.
- Komutlar 32 bit RV32I makine koduna dönüştürülür.
- Binary değerlerin hexadecimal karşılıkları oluşturulur.

## Desteklenen Komut Formatları

Projede RV32I mimarisindeki farklı komut formatları kullanılmaktadır.

### R-Type

Örnek desteklenen komutlar:

- `add`
- `sub`
- `and`
- `or`
- `xor`

### I-Type

Örnek desteklenen komutlar:

- `addi`
- `lw`
- `jalr`

### S-Type

Desteklenen store komutu:

- `sw`

### B-Type

Desteklenen branch komutları:

- `beq`
- `bne`

### J-Type

Desteklenen jump komutu:

- `jal`

## Opcode Table

Opcode Table, RV32I komutlarının kodlama için gerekli bilgilerini saklamaktadır.

Her kayıt içerisinde aşağıdaki bilgiler bulunabilir:

- Mnemonic
- Instruction Format
- Opcode
- funct3
- funct7

Opcode Table bağlı liste tabanlı olarak geliştirilmiştir.

## Symbol Table

Symbol Table assembly kaynak kodundaki sembollerin adreslerini ve türlerini saklamaktadır.

Semboller üç farklı türde değerlendirilebilir:

- `LOCAL`
- `GLOBAL`
- `EXTERN`

Assembler tarafından oluşturulan sembol tabloları daha sonra Linker işlemlerinde kullanılmaktadır.

## Global ve External Semboller

Birden fazla assembly modülünün birbirleriyle iletişim kurabilmesi için global ve external semboller desteklenmektedir.

`.global` ile başka modüllerin kullanabileceği semboller tanımlanabilir.

Örneğin:

    .global fonksiyon

`.extern` ile başka bir modülde tanımlanan sembole referans verilebilir.

Örneğin:

    .extern fonksiyon

Assembler external sembolün kesin adresini bilmiyorsa ilgili komut için relocation kaydı oluşturur.

## Nesne Dosyaları

Her assembly modülü bağımsız olarak assemble edilerek bir nesne dosyasına dönüştürülmektedir.

Projede oluşturulan nesne dosyaları:

    main_nesne.obj
    fonk_nesne.obj

Nesne dosyaları içerisinde program bilgileri, makine kodları, semboller ve relocation kayıtları bulunmaktadır.

Kullanılan kayıt türleri arasında:

- Header Record
- Definition Record
- Reference Record
- Text Record
- Modification Record
- End Record

bulunmaktadır.

## Relocation Table

Assembler, adresi assembly aşamasında kesin olarak bilinmeyen external semboller için relocation kayıtları oluşturur.

Relocation kaydı içerisinde örneğin:

- Komut adresi
- Hedef sembol
- Komut tipi
- Mnemonic
- Register bilgileri

saklanmaktadır.

Projede özellikle B-Type ve J-Type komutları için relocation işlemleri gerçekleştirilmektedir.

## Linker Çalışma Mantığı

Linker farklı nesne dosyalarını birleştirerek tek bir çalıştırılabilir makine kodu oluşturmaktadır.

İşlem temel olarak şu şekilde gerçekleştirilir:

1. Nesne dosyaları okunur.
2. Text segmentleri birleştirilir.
3. Global semboller ve kesin adresleri belirlenir.
4. Relocation kayıtları toplanır.
5. External sembollerin adresleri Global Symbol Table üzerinden bulunur.
6. Branch ve jump offset değerleri yeniden hesaplanır.
7. İlgili makine kodları güncellenir.
8. Son hexadecimal makine kodu oluşturulur.

## Global Symbol Table

Linker farklı modüllerde tanımlanan global sembollerin kesin adreslerini hesaplar.

Bu bilgiler:

    global_symbol.txt

dosyasına yazılmaktadır.

Global Symbol Table sayesinde farklı assembly dosyalarında bulunan fonksiyon ve label referansları çözülebilmektedir.

## B-Type Relocation

`beq` ve `bne` gibi branch komutlarında hedef external bir sembol olduğunda assembler başlangıçta kesin offset değerini bilemez.

Linker hedef sembolün kesin adresini öğrendikten sonra:

    offset = target_address - relocation_address

hesabını gerçekleştirir.

Daha sonra B-Type immediate alanları yeniden oluşturularak makine kodu güncellenir.

## J-Type Relocation

`jal` komutu external bir sembole yöneliyorsa benzer şekilde relocation kaydı oluşturulur.

Linker hedef sembolün kesin adresini belirledikten sonra J-Type offset değerini hesaplar ve `jal` komutunun makine kodunu yeniden oluşturur.

## Final Makine Kodu

Tüm nesne dosyaları birleştirilip relocation işlemleri tamamlandıktan sonra son makine kodu:

    linker/makine_kodu.hex

dosyasına yazılmaktadır.

Dosyada her RV32I komutu hexadecimal formatta bulunmaktadır.

## Hata Kontrolleri

Projede çeşitli temel kontroller bulunmaktadır.

Örneğin:

- Geçersiz register kontrolü
- Register aralığı kontrolü
- Desteklenmeyen komut kontrolü
- Hatalı operand kontrolü
- Çözülemeyen external sembol kontrolü
- Geçersiz instruction format kontrolü

RV32I register değerleri `x0` ile `x31` arasında kontrol edilmektedir.

## Kullanılan Teknolojiler

- Python
- Jupyter Notebook
- RISC-V
- RV32I Instruction Set
- Assembly Language
- Two-Pass Assembler
- Linker
- Relocation
- Symbol Table
- Global Symbol Table
- Opcode Table
- Linked List
- Object Files
- Binary Encoding
- Hexadecimal Encoding

## Çalıştırma

Assembler bölümünü incelemek için:

    sistem_programlama_kod (1).ipynb

Jupyter Notebook dosyası açılarak hücreler sırasıyla çalıştırılabilir.

Linker bölümünü çalıştırmak için `linker` klasöründe:

    python kodlar.py

komutu kullanılabilir.

Program çalıştırıldığında:

- `main.asm` assemble edilir.
- `fonksiyon.asm` assemble edilir.
- Nesne dosyaları oluşturulur.
- Sembol tabloları oluşturulur.
- Nesne dosyaları Linker'a eklenir.
- Global semboller hesaplanır.
- Relocation işlemleri gerçekleştirilir.
- Final makine kodu oluşturulur.

## Projenin Amacı

Bu projenin amacı assembler ve linker çalışma prensiplerinin uygulamalı olarak öğrenilmesidir.

İlk aşamada Two-Pass Assembler kullanılarak RV32I assembly komutlarının makine koduna dönüştürülmesi gerçekleştirilmiştir.

İkinci aşamada ise farklı assembly modüllerinin bağımsız olarak assemble edilmesi, external ve global sembollerin yönetilmesi, relocation kayıtlarının oluşturulması ve Linker tarafından bu kayıtların çözülmesi gerçekleştirilmiştir.

Bu sayede kaynak assembly kodundan başlayarak nesne dosyalarının oluşturulması, modüllerin bağlanması ve son makine kodunun üretilmesine kadar olan temel toolchain süreci uygulanmıştır.

## Proje Notu

Bu proje Sistem Programlama dersi kapsamında geliştirilen akademik bir çalışmadır.
