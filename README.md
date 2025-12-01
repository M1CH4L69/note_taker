# Smart Note Taker (Threaded) — Komplexní Dokumentace

---

## 1. Informace o projektu

| Údaj | Popis |
|------|-------|
| **Název projektu** | Smart Note Taker (Threaded) |
| **Autor** | Michal Němec, c4b |
| **Datum vypracování** | Listopad 2025 |
| **Typ projektu** | Školní projekt |
| **Účel** | Demonstrace práce s vlákny (threading) a synchronizací v Pythonu |

---

## 2. Specifikace požadavků (Business & Functional Requirements)

### 2.1 Funkční požadavky (FR)

- **FR1:** Menu se 4 volbami: Add, View, Delete, Exit
- **FR2:** Při přidání se zadává obsah a důležitost (y/n)
- **FR3:** Každá poznámka má timestamp (YYYY-MM-DD HH:MM:SS)
- **FR4:** Analýza: počet slov, priorita (URGENT/Normal), log zápis
- **FR5:** Analýza běží 2 sec (simulace náročné operace) v background
- **FR6:** Zálohování každých 10 sec bez blokování
- **FR7:** Graceful shutdown — korektní zastavení vláken

---

## 3. Architektura aplikace

### Přehled

Aplikace má 3 vlákna:
- **Main Thread** — menu, vstup, create/stop vláken
- **Analyzer Thread** — čeká na úkoly, analyzuje (2 sec), zapisuje log
- **Backup Thread** — každých 10 sec kopíruje notes.txt → notes.bak

Synchronizace:
- `analysis_queue` (Queue) — Producer-Consumer
- `print_lock` (Lock) — Mutex pro stdout
- `stop_event` (Event) — Signal pro zastavení

Data:
- `notes.txt` — primární data
- `notes.bak` — záloha
- `analysis_log.txt` — log analýz


---

## 4. Běh aplikace (Use Cases & Behavioral Diagrams)

### Typický scénář — Přidání poznámky

1. Uživatel vybere «1. Add Note»
2. Vstup: obsah poznámky + důležitost (y/n)
3. Aplikace: zápíše do notes.txt + pošle do analysis_queue
4. Main vlákno vrátí do menu (nečeká)
5. Analyzer vlákno: vezme z fronty, čeká 2 sec (simulace analýzy), počítá slova, zapisuje do analysis_log.txt
6. UI zůstává responsivní (Analyzer běží na pozadí)

### Graceful Shutdown

1. Uživatel vybere «4. Exit»
2. Main vlákno: nastaví `stop_event`
3. Main vlákno: pošle `None` do analysis_queue (Sentinel)
4. Backup vlákno: slyší stop_event, skončí
5. Analyzer vlákno: slyší None, skončí
6. Main vlákno: zavolá join() na obě vlákna
7. Aplikace bezpečně terminuje

---

## 5. Rozhraní, protokoly a závislosti

### 5.1 Standardní knihovny Python

| Modul | Funkce |
|-------|--------|
| `os` | Detekce OS, clear screen |
| `time` | sleep(), strftime() — čekání a razítka |
| `threading` | Thread, Lock, Event — konkurence |
| `queue` | Queue — thread-safe fronta |
| `shutil` | copy() — kopírování souborů |

---

## 6. Konfigurace

### Konfigurační parametry (hardcoded)

| Parametr | Hodnota | Funkce |
|----------|---------|--------|
| Backup interval | 10 sec | `backup_scheduler()` |
| Analysis delay | 2 sec | `note_analyzer_worker()` |
| Primary file | `notes.txt` | `addnote()` |
| Backup file | `notes.bak` | `backup_scheduler()` |
| Log file | `analysis_log.txt` | `note_analyzer_worker()` |

---

## 7. Instalace a spuštění

### 7.1 Požadavky

- **Python:** 3.11+
- **OS:** Windows, Linux, macOS
- **Disk:** 5 MB

### 7.2 Postup

```powershell
cd d:\PythonAcademi\webinar15_16_todoList\TO_DO_project1
python --version          # Ověření Python 3.11+
python -m venv .venv      # Virtuální prostředí (doporučeno)
.\.venv\Scripts\Activate.ps1
python main.py            # Spuštění
```

### 7.3 Ověření

Po spuštění vidíte menu:
```
System started. Background threads running...

=== SMART NOTE TAKER (Threaded) ===
1. Add Note (Triggers Background Analysis)
2. View Notes
3. Delete Note
4. Exit
Choose an option (1-4): 
```

---

## 8. Chybové stavy

| Chyba | Řešení |
|-------|--------|
| `ModuleNotFoundError` | Zkontrolujte Python 3.11+ |
| `FileNotFoundError: main.py` | Spuštějte z správného adresáře |
| `PermissionError` | Zavřete soubor, ověřte práva |
| Zamíchané výstupy | Aplikace má mutex; restartujte |

9. Testování
   Test chybějícího souboru
   Test čtení jedné poznámky

---

**Závěr:** Aplikace **splňuje všechny požadavky** a je **připravena.**

---


# Spuštění aplikace
python main.py
```

Použití
- Po spuštění se objeví menu s volbami:
  - `1` Add Note — přidání nové poznámky a odeslání do pozadní analýzy
  - `2` View Notes — zobrazení uložených poznámek
  - `3` Delete Note — smazání vybrané poznámky
  - `4` Exit — ukončení aplikace a korektní zastavení vláken

Poznámky k implementaci
- Aplikace používá dvě pozadní vlákna: jeden worker pro analýzu poznámek (zapisuje do `analysis_log.txt`) a druhý pro pravidelné zálohování `notes.txt` do `notes.bak`.
- Aplikace běžně vytvoří soubory `notes.txt`, `notes.bak` a `analysis_log.txt` v aktuálním pracovním adresáři.
