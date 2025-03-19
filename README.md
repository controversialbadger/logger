# Zaawansowany Walidator Emaili

Program zaawansowanego walidatora emaili w Pythonie, który szybko i efektywnie sprawdza poprawność adresów email. Oferuje walidację pojedynczych adresów oraz przetwarzanie wsadowe z plików.

## Funkcje

- Szybka walidacja z wykorzystaniem wyrażeń regularnych przed kosztownymi operacjami
- Asynchroniczne przetwarzanie dla zwiększenia wydajności
- Pamięć podręczna dla wyników walidacji domen (unikanie powtórnych sprawdzeń)
- Sprawdzanie poprawności składni emaila (format `nazwa@domena.com`)
- Weryfikacja czy domena emaila może otrzymywać wiadomości (sprawdzenie rekordów MX)
- Wsparcie dla przetwarzania wsadowego z plików
- Wskaźniki postępu dla operacji wsadowych
- Statystyki czasu wykonania
- Opcja pomijania sprawdzania rekordów MX dla szybszej walidacji

## Wymagania

- Python 3.7 lub nowszy
- Biblioteki:
  - `email-validator`
  - `dnspython`

## Instalacja

1. Upewnij się, że masz zainstalowany Python 3.7 lub nowszy
2. Zainstaluj wymagane biblioteki:

```bash
pip install -r requirements.txt
```

## Użycie

### Tryb interaktywny

```bash
python email_validator.py
```

### Walidacja pojedynczego adresu email

```bash
python email_validator.py --email jan.kowalski@gmail.com
```

### Przetwarzanie wsadowe z pliku

```bash
python email_validator.py -f lista_emaili.txt -o poprawne_emaile.txt
```

### Szybka walidacja (bez sprawdzania rekordów MX)

```bash
python email_validator.py --email jan.kowalski@gmail.com --no-mx
```

### Pełna lista opcji

```
usage: email_validator.py [-h] [-f FILE] [-o OUTPUT] [--no-mx] [--email EMAIL]

Zaawansowany walidator adresów email

optional arguments:
  -h, --help            Wyświetl pomoc
  -f FILE, --file FILE  Plik z adresami email (jeden na linię)
  -o OUTPUT, --output OUTPUT
                        Plik wyjściowy dla poprawnych adresów
  --no-mx               Pomiń sprawdzanie rekordów MX (szybsza walidacja)
  --email EMAIL         Pojedynczy adres email do walidacji
```

## Przykład użycia

### Tryb interaktywny

```
=== Zaawansowany Walidator Emaili ===
Wprowadź adres email (lub wpisz 'exit', aby zakończyć):
> jan.kowalski@gmail.com
Email 'jan.kowalski@gmail.com' jest poprawny. (czas: 0.1234s)
> niepoprawny@email
Email 'niepoprawny@email' jest niepoprawny. Powód: The domain name niepoprawny@email is not valid. It should have a period. (czas: 0.0123s)
> anna.nowak@example.com
Email 'anna.nowak@example.com' jest poprawny. (czas: 0.1345s)
> exit

Prawidłowe adresy email:
- jan.kowalski@gmail.com
- anna.nowak@example.com
```

### Przetwarzanie wsadowe

```
$ python email_validator.py -f emaile.txt -o poprawne.txt
Walidacja 100 adresów email...
Postęp: [100/100] 100.0%
Czas walidacji: 5.23 sekund
Średni czas na email: 0.0523 sekund
Zwalidowano 100 adresów email, z czego 75 jest poprawnych (75.0%)
Zapisano 75 poprawnych adresów do pliku poprawne.txt
```

## Wydajność

Program został zoptymalizowany pod kątem szybkości działania:

1. Wstępna walidacja z użyciem wyrażeń regularnych przed kosztownymi operacjami
2. Asynchroniczne przetwarzanie dla równoległej walidacji wielu adresów
3. Pamięć podręczna dla wyników walidacji domen
4. Opcja pomijania sprawdzania rekordów MX dla najszybszej walidacji