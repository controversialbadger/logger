# Email Validator

Program walidatora emaili w Pythonie, który przyjmuje adresy email od użytkownika, sprawdza ich poprawność i zwraca listę tylko prawidłowych adresów po zakończeniu wprowadzania.

## Funkcje

- Przyjmowanie adresów email jeden po drugim
- Sprawdzanie poprawności składni emaila (format `nazwa@domena.com`)
- Weryfikacja czy domena emaila może otrzymywać wiadomości (sprawdzenie rekordów MX)
- Wyświetlanie listy prawidłowych adresów email po zakończeniu wprowadzania

## Wymagania

- Python 3.6 lub nowszy
- Biblioteka `email-validator`

## Instalacja

1. Upewnij się, że masz zainstalowany Python 3.6 lub nowszy
2. Zainstaluj wymaganą bibliotekę:

```bash
pip install email-validator
```

## Użycie

1. Uruchom program:

```bash
python email_validator.py
```

2. Wprowadź adresy email jeden po drugim
3. Aby zakończyć wprowadzanie, wpisz `exit`
4. Program wyświetli listę prawidłowych adresów email

## Przykład użycia

```
=== Walidator emaili ===
Wprowadź adres email (lub wpisz 'exit', aby zakończyć):
> jan.kowalski@gmail.com
Email 'jan.kowalski@gmail.com' jest poprawny.
> niepoprawny@email
Email 'niepoprawny@email' jest niepoprawny. Powód: The domain name niepoprawny@email is not valid. It should have a period.
> anna.nowak@example.com
Email 'anna.nowak@example.com' jest poprawny.
> exit

Prawidłowe adresy email:
- jan.kowalski@gmail.com
- anna.nowak@example.com
```