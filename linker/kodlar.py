import os


# =========================================================
# LINKED LIST TABANLI OPCODE TABLE
# =========================================================

class OpcodeNode:
    def __init__(self, mnemonic, fmt, opcode, funct3="", funct7=""):
        self.mnemonic = mnemonic
        self.fmt = fmt
        self.opcode = opcode
        self.funct3 = funct3
        self.funct7 = funct7
        self.next = None


class OpcodeTable:
    def __init__(self):
        self.head = None

    def add(self, mnemonic, fmt, opcode, funct3="", funct7=""):
        node = OpcodeNode(mnemonic, fmt, opcode, funct3, funct7)

        if self.head is None:
            self.head = node
            return

        current = self.head
        while current.next is not None:
            current = current.next

        current.next = node

    def find(self, mnemonic):
        current = self.head

        while current is not None:
            if current.mnemonic == mnemonic:
                return current
            current = current.next

        return None


# =========================================================
# LINKED LIST TABANLI SYMBOL TABLE
# =========================================================

class SymbolNode:
    def __init__(self, label, address, sym_type="LOCAL"):
        self.label = label
        self.address = address
        self.sym_type = sym_type
        self.next = None


class SymbolTable:
    def __init__(self):
        self.head = None

    def add(self, label, address, sym_type="LOCAL"):
        existing = self.find(label)

        if existing is not None:
            existing.address = address
            existing.sym_type = sym_type
            return

        node = SymbolNode(label, address, sym_type)

        if self.head is None:
            self.head = node
            return

        current = self.head
        while current.next is not None:
            current = current.next

        current.next = node

    def find(self, label):
        current = self.head

        while current is not None:
            if current.label == label:
                return current
            current = current.next

        return None

    def get_all(self):
        result = {}
        current = self.head

        while current is not None:
            result[current.label] = {
                "address": current.address,
                "type": current.sym_type
            }
            current = current.next

        return result


# =========================================================
# RELOCATION TABLE
# =========================================================

class RelocationNode:
    def __init__(self, address, label, instr_type, mnemonic, rd="", rs1="", rs2=""):
        self.address = address
        self.label = label
        self.instr_type = instr_type
        self.mnemonic = mnemonic
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.next = None


class RelocationTable:
    def __init__(self):
        self.head = None

    def add(self, address, label, instr_type, mnemonic, rd="", rs1="", rs2=""):
        node = RelocationNode(address, label, instr_type, mnemonic, rd, rs1, rs2)

        if self.head is None:
            self.head = node
            return

        current = self.head
        while current.next is not None:
            current = current.next

        current.next = node

    def get_all_list(self):
        result = []
        current = self.head

        while current is not None:
            result.append({
                "address": current.address,
                "label": current.label,
                "type": current.instr_type,
                "mnemonic": current.mnemonic,
                "rd": current.rd,
                "rs1": current.rs1,
                "rs2": current.rs2
            })
            current = current.next

        return result


# =========================================================
# ASSEMBLER
# =========================================================

class Assembler:
    def __init__(self):
        self.symbols = SymbolTable()
        self.relocations = RelocationTable()
        self.opcodes = OpcodeTable()
        self.text_segment = []
        self.global_names = []
        self.extern_names = []
        self.load_default_opcodes()

    def load_default_opcodes(self):
        self.opcodes.add("add",  "R", "0110011", "000", "0000000")
        self.opcodes.add("sub",  "R", "0110011", "000", "0100000")
        self.opcodes.add("and",  "R", "0110011", "111", "0000000")
        self.opcodes.add("or",   "R", "0110011", "110", "0000000")
        self.opcodes.add("xor",  "R", "0110011", "100", "0000000")

        self.opcodes.add("addi", "I", "0010011", "000")
        self.opcodes.add("lw",   "I", "0000011", "010")
        self.opcodes.add("jalr", "I", "1100111", "000")

        self.opcodes.add("sw",   "S", "0100011", "010")

        self.opcodes.add("beq",  "B", "1100011", "000")
        self.opcodes.add("bne",  "B", "1100011", "001")

        self.opcodes.add("jal",  "J", "1101111")

    def clean_line(self, line):
        hash_pos = line.find("#")
        semicolon_pos = line.find(";")

        cut_pos = -1

        if hash_pos != -1 and semicolon_pos != -1:
            cut_pos = min(hash_pos, semicolon_pos)
        elif hash_pos != -1:
            cut_pos = hash_pos
        elif semicolon_pos != -1:
            cut_pos = semicolon_pos

        if cut_pos != -1:
            line = line[:cut_pos]

        return line.strip()

    def parse_register(self, token):
        token = token.strip()

        if not token.startswith("x"):
            raise ValueError(f"Geçersiz register: {token}")

        number = int(token[1:])

        if number < 0 or number > 31:
            raise ValueError(f"Register aralık dışı: {token}")

        return format(number, "05b")

    def to_twos_complement(self, value, bits):
        return value & ((1 << bits) - 1)

    def encode_branch_binary(self, mnemonic, rs1_bin, rs2_bin, offset):
        node = self.opcodes.find(mnemonic)

        imm13 = self.to_twos_complement(offset, 13)

        bit12 = (imm13 >> 12) & 1
        bit11 = (imm13 >> 11) & 1
        bits10_5 = (imm13 >> 5) & 0b111111
        bits4_1 = (imm13 >> 1) & 0b1111

        return (
            format(bit12, "01b")
            + format(bits10_5, "06b")
            + rs2_bin
            + rs1_bin
            + node.funct3
            + format(bits4_1, "04b")
            + format(bit11, "01b")
            + node.opcode
        )

    def encode_jal_binary(self, rd_bin, offset):
        opcode = "1101111"

        imm21 = self.to_twos_complement(offset, 21)

        bit20 = (imm21 >> 20) & 1
        bits10_1 = (imm21 >> 1) & 0b1111111111
        bit11 = (imm21 >> 11) & 1
        bits19_12 = (imm21 >> 12) & 0b11111111

        return (
            format(bit20, "01b")
            + format(bits10_1, "010b")
            + format(bit11, "01b")
            + format(bits19_12, "08b")
            + rd_bin
            + opcode
        )

    def pass1(self, input_file):
        pc = 0

        with open(input_file, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = self.clean_line(raw_line)

                if line == "":
                    continue

                if line.startswith(".global"):
                    name = line.split()[1].strip()
                    self.global_names.append(name)
                    continue

                if line.startswith(".extern"):
                    name = line.split()[1].strip()
                    self.extern_names.append(name)
                    self.symbols.add(name, 0, "EXTERN")
                    continue

                if ":" in line:
                    label, rest = line.split(":", 1)
                    label = label.strip()

                    if label in self.global_names:
                        sym_type = "GLOBAL"
                    else:
                        sym_type = "LOCAL"

                    self.symbols.add(label, pc, sym_type)
                    line = rest.strip()

                if line == "" or line.startswith("."):
                    continue

                pc += 4

    def encode_instruction(self, mnemonic, operands, pc):
        node = self.opcodes.find(mnemonic)

        if node is None:
            raise ValueError(f"Bilinmeyen komut: {mnemonic}")

        if node.fmt == "R":
            rd = self.parse_register(operands[0])
            rs1 = self.parse_register(operands[1])
            rs2 = self.parse_register(operands[2])

            return node.funct7 + rs2 + rs1 + node.funct3 + rd + node.opcode

        if node.fmt == "I":
            if mnemonic == "lw":
                rd = self.parse_register(operands[0])
                imm, rs1_text = operands[1].replace(")", "").split("(")
                rs1 = self.parse_register(rs1_text)
                imm_bin = format(self.to_twos_complement(int(imm), 12), "012b")
            else:
                rd = self.parse_register(operands[0])
                rs1 = self.parse_register(operands[1])
                imm_bin = format(self.to_twos_complement(int(operands[2]), 12), "012b")

            return imm_bin + rs1 + node.funct3 + rd + node.opcode

        if node.fmt == "S":
            rs2 = self.parse_register(operands[0])
            imm, rs1_text = operands[1].replace(")", "").split("(")
            rs1 = self.parse_register(rs1_text)

            imm_bin = format(self.to_twos_complement(int(imm), 12), "012b")
            imm_high = imm_bin[:7]
            imm_low = imm_bin[7:]

            return imm_high + rs2 + rs1 + node.funct3 + imm_low + node.opcode

        if node.fmt == "B":
            rs1 = self.parse_register(operands[0])
            rs2 = self.parse_register(operands[1])
            target = operands[2].strip()

            symbol = self.symbols.find(target)

            if symbol is not None and symbol.sym_type != "EXTERN":
                offset = symbol.address - pc
            else:
                offset = 0
                self.relocations.add(pc, target, "B", mnemonic, "", rs1, rs2)

            return self.encode_branch_binary(mnemonic, rs1, rs2, offset)

        if node.fmt == "J":
            if len(operands) == 1:
                rd = self.parse_register("x1")
                target = operands[0].strip()
            else:
                rd = self.parse_register(operands[0])
                target = operands[1].strip()

            symbol = self.symbols.find(target)

            if symbol is not None and symbol.sym_type != "EXTERN":
                offset = symbol.address - pc
            else:
                offset = 0
                self.relocations.add(pc, target, "J", mnemonic, rd)

            return self.encode_jal_binary(rd, offset)

        raise ValueError(f"Desteklenmeyen format: {node.fmt}")

    def assemble(self, input_file, output_obj_file):
        self.pass1(input_file)

        pc = 0
        self.text_segment = []

        with open(input_file, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = self.clean_line(raw_line)

                if line == "":
                    continue

                if line.startswith(".global") or line.startswith(".extern"):
                    continue

                if ":" in line:
                    line = line.split(":", 1)[1].strip()

                if line == "" or line.startswith("."):
                    continue

                parts = line.split(None, 1)
                mnemonic = parts[0]

                if len(parts) > 1:
                    operands = [op.strip() for op in parts[1].split(",")]
                else:
                    operands = []

                binary_code = self.encode_instruction(mnemonic, operands, pc)
                self.text_segment.append(binary_code)
                pc += 4

        prog_name = os.path.basename(input_file)[:6].upper()

        with open(output_obj_file, "w", encoding="utf-8") as f:
            f.write(f"H{prog_name:<6}000000{len(self.text_segment) * 4:06X}\n")

            globals_list = [
                name for name, info in self.symbols.get_all().items()
                if info["type"] == "GLOBAL"
            ]

            if globals_list:
                d_line = "D"
                for name in globals_list:
                    d_line += f"{name[:6]:<6}{self.symbols.find(name).address:06X}"
                f.write(d_line + "\n")

            externs_list = [
                name for name, info in self.symbols.get_all().items()
                if info["type"] == "EXTERN"
            ]

            if externs_list:
                r_line = "R"
                for name in externs_list:
                    r_line += f"{name[:6]:<6}"
                f.write(r_line + "\n")

            hex_text = ""
            for binary in self.text_segment:
                hex_text += f"{int(binary, 2):08X}"

            f.write(f"T000000{len(self.text_segment) * 4:02X}{hex_text}\n")

            for r in self.relocations.get_all_list():
                if r["type"] == "B":
                    f.write(
                        f"M{r['address']:06X}B+{r['label'][:6]:<6}"
                        f"|{r['mnemonic']}|{r['rs1']}|{r['rs2']}\n"
                    )

                elif r["type"] == "J":
                    f.write(
                        f"M{r['address']:06X}J+{r['label'][:6]:<6}"
                        f"|{r['mnemonic']}|{r['rd']}\n"
                    )

            f.write("E000000\n")

        print(f"Nesne dosyası oluşturuldu: {output_obj_file}")

    def save_symbols_to_txt(self, output_file):
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"{'Sembol':<15} | {'Adres':<10} | {'Tip':<10}\n")
            f.write("-" * 45 + "\n")

            for label, info in self.symbols.get_all().items():
                f.write(f"{label:<15} | 0x{info['address']:08X} | {info['type']:<10}\n")

        print(f"Sembol tablosu dosyası oluşturuldu: {output_file}")


# =========================================================
# LINKER
# =========================================================

class Linker:
    def __init__(self, text_base=0x0000):
        self.text_base = text_base
        self.merged_text = []
        self.global_symbols = {}
        self.reloc_queue = []

    def to_twos_complement(self, value, bits):
        return value & ((1 << bits) - 1)

    def encode_branch_hex(self, mnemonic, rs1_bin, rs2_bin, offset):
        if mnemonic == "beq":
            funct3 = "000"
        elif mnemonic == "bne":
            funct3 = "001"
        else:
            raise ValueError(f"Desteklenmeyen branch komutu: {mnemonic}")

        opcode = "1100011"

        imm13 = self.to_twos_complement(offset, 13)

        bit12 = (imm13 >> 12) & 1
        bit11 = (imm13 >> 11) & 1
        bits10_5 = (imm13 >> 5) & 0b111111
        bits4_1 = (imm13 >> 1) & 0b1111

        binary = (
            format(bit12, "01b")
            + format(bits10_5, "06b")
            + rs2_bin
            + rs1_bin
            + funct3
            + format(bits4_1, "04b")
            + format(bit11, "01b")
            + opcode
        )

        return f"{int(binary, 2):08X}"

    def encode_jal_hex(self, rd_bin, offset):
        opcode = "1101111"

        imm21 = self.to_twos_complement(offset, 21)

        bit20 = (imm21 >> 20) & 1
        bits10_1 = (imm21 >> 1) & 0b1111111111
        bit11 = (imm21 >> 11) & 1
        bits19_12 = (imm21 >> 12) & 0b11111111

        binary = (
            format(bit20, "01b")
            + format(bits10_1, "010b")
            + format(bit11, "01b")
            + format(bits19_12, "08b")
            + rd_bin
            + opcode
        )

        return f"{int(binary, 2):08X}"

    def add_object(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_offset = len(self.merged_text) * 4

        for line in lines:
            line = line.strip()

            if line == "":
                continue

            record_type = line[0]

            if record_type == "D":
                for i in range(1, len(line), 12):
                    name = line[i:i + 6].strip()
                    addr_text = line[i + 6:i + 12].strip()

                    if name == "" or addr_text == "":
                        continue

                    local_addr = int(addr_text, 16)
                    final_addr = self.text_base + current_offset + local_addr

                    self.global_symbols[name] = final_addr

            elif record_type == "T":
                hex_data = line[9:].strip()

                for i in range(0, len(hex_data), 8):
                    word = hex_data[i:i + 8]

                    if len(word) == 8:
                        self.merged_text.append(word)

            elif record_type == "M":
                local_addr = int(line[1:7], 16)
                reloc_type = line[7]
                sign = line[8]
                label = line[9:15].strip()

                parts = line.split("|")

                relocation = {
                    "address": current_offset + local_addr,
                    "type": reloc_type,
                    "sign": sign,
                    "label": label
                }

                if reloc_type == "B":
                    relocation["mnemonic"] = parts[1]
                    relocation["rs1"] = parts[2]
                    relocation["rs2"] = parts[3]

                if reloc_type == "J":
                    relocation["mnemonic"] = parts[1]
                    relocation["rd"] = parts[2]

                self.reloc_queue.append(relocation)

    def resolve_relocations(self):
        for r in self.reloc_queue:
            label = r["label"]

            if label not in self.global_symbols:
                raise ValueError(f"Çözülemeyen external sembol: {label}")

            target_addr = self.global_symbols[label]
            reloc_addr = r["address"]

            index = reloc_addr // 4

            if r["type"] == "B":
                offset = target_addr - reloc_addr
                new_hex = self.encode_branch_hex(
                    r["mnemonic"],
                    r["rs1"],
                    r["rs2"],
                    offset
                )
                self.merged_text[index] = new_hex

            elif r["type"] == "J":
                offset = target_addr - reloc_addr
                new_hex = self.encode_jal_hex(
                    r["rd"],
                    offset
                )
                self.merged_text[index] = new_hex

            print(
                f"Bağlama yapıldı: {label} "
                f"reloc=0x{reloc_addr:06X} "
                f"target=0x{target_addr:06X} "
                f"new={self.merged_text[index]}"
            )

    def generate_hex(self, output_file):
        with open(output_file, "w", encoding="utf-8") as f:
            for code in self.merged_text:
                f.write(code + "\n")

        print(f"Final makine kodu dosyası oluşturuldu: {output_file}")

    def save_global_symbols_to_txt(self, output_file):
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"{'Global Sembol':<15} | {'Kesin Adres':<12}\n")
            f.write("-" * 35 + "\n")

            for label, addr in self.global_symbols.items():
                f.write(f"{label:<15} | 0x{addr:08X}\n")

        print(f"Global sembol tablosu dosyası oluşturuldu: {output_file}")


# =========================================================
# ÇALIŞTIRMA BLOĞU
# =========================================================

if __name__ == "__main__":
    path = os.getcwd()

    asm_main = Assembler()
    asm_main.assemble(
        os.path.join(path, "main.asm"),
        os.path.join(path, "main_nesne.obj")
    )
    asm_main.save_symbols_to_txt(os.path.join(path, "main_symbol.txt"))

    asm_fonk = Assembler()
    asm_fonk.assemble(
        os.path.join(path, "fonksiyon.asm"),
        os.path.join(path, "fonk_nesne.obj")
    )
    asm_fonk.save_symbols_to_txt(os.path.join(path, "fonk_symbol.txt"))

    linker = Linker()
    linker.add_object(os.path.join(path, "main_nesne.obj"))
    linker.add_object(os.path.join(path, "fonk_nesne.obj"))
    linker.resolve_relocations()
    linker.save_global_symbols_to_txt(os.path.join(path, "global_symbol.txt"))
    linker.generate_hex(os.path.join(path, "makine_kodu.hex"))