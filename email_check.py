import asyncio
import re
import time
import os
import argparse
import smtplib
from email_validator import validate_email, EmailNotValidError
from validate_email import validate_email as verify_email_exists
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple, Set, Optional, Union

# Regular expression for basic email validation
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Cache for domain validation results
domain_cache: Dict[str, bool] = {}

def quick_validate(email: str) -> bool:
    """
    Quickly validate email format using regex before more expensive checks.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if the email passes basic format validation
    """
    return bool(EMAIL_REGEX.match(email))

async def check_email_exists(email: str) -> Tuple[bool, Optional[str]]:
    """
    Check if an email address actually exists by verifying with the mail server.
    
    Args:
        email (str): The email address to check
        
    Returns:
        tuple: (exists, error_message) where:
            - exists (bool): True if email exists, False otherwise
            - error_message (Optional[str]): Error message if applicable
    """
    try:
        # Run the CPU-bound validation in a thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            # verify_email_exists checks if the email exists on the mail server
            exists = await loop.run_in_executor(
                pool, 
                lambda: verify_email_exists(
                    email,
                    check_format=False,  # We already checked format
                    check_dns=False,     # We already checked DNS
                    check_smtp=True,     # Check SMTP
                    smtp_timeout=10,     # Timeout in seconds
                    smtp_helo_host='my.host.name',  # HELO hostname
                    smtp_from_address='verify@example.com',  # MAIL FROM address
                    smtp_skip_tls=False, # Don't skip TLS
                    smtp_tls_context=None, # Use default TLS context
                    smtp_debug=False     # Don't show debug info
                )
            )
        
        if exists:
            return True, None
        else:
            return False, "Adres email nie istnieje na serwerze pocztowym"
    except Exception as e:
        return False, f"Błąd podczas weryfikacji istnienia adresu email: {str(e)}"

async def validate_email_async(email: str, check_deliverability: bool = True, check_existence: bool = False) -> Tuple[bool, str, Optional[str]]:
    """
    Asynchronously validate an email address.
    
    Args:
        email (str): The email address to validate
        check_deliverability (bool): Whether to check MX records
        check_existence (bool): Whether to check if the email actually exists
        
    Returns:
        tuple: (is_valid, result, warning) where:
            - is_valid (bool): True if email is valid, False otherwise
            - result (str): Normalized email if valid, error message if invalid
            - warning (Optional[str]): Warning message if applicable
    """
    # Quick validation first
    if not quick_validate(email):
        return False, "Niepoprawny format adresu email", None
    
    # Extract domain for cache lookup
    try:
        domain = email.split('@')[1]
    except IndexError:
        return False, "Brak znaku @ w adresie email", None
    
    # Check for common disposable email domains
    disposable_domains = [
        'tempmail.com', 'throwawaymail.com', 'mailinator.com', 
        'guerrillamail.com', 'yopmail.com', 'temp-mail.org',
        'fakeinbox.com', '10minutemail.com', 'trashmail.com'
    ]
    
    if domain.lower() in disposable_domains:
        return False, f"Domena {domain} jest tymczasową domeną email", None
    
    # Check cache for domain validation result
    if check_deliverability and domain in domain_cache:
        if not domain_cache[domain]:
            return False, f"Domena {domain} nie może odbierać wiadomości (z pamięci podręcznej)", None
    
    # Perform full validation
    try:
        # Run the CPU-bound validation in a thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            valid = await loop.run_in_executor(
                pool, 
                lambda: validate_email(email, check_deliverability=check_deliverability)
            )
        
        # Cache the domain result
        if check_deliverability:
            domain_cache[domain] = True
        
        warning = "UWAGA: Walidacja sprawdza tylko czy domena może odbierać wiadomości, nie weryfikuje czy konkretny adres email istnieje."
        return True, valid.normalized, warning
    except EmailNotValidError as e:
        # Cache the negative result
        if check_deliverability and domain not in domain_cache:
            domain_cache[domain] = False
        return False, str(e), None

async def batch_validate(emails: List[str], check_deliverability: bool = True, 
                         show_progress: bool = True) -> Dict[str, Dict[str, Union[bool, str, Optional[str]]]]:
    """
    Validate multiple email addresses concurrently.
    
    Args:
        emails (List[str]): List of email addresses to validate
        check_deliverability (bool): Whether to check MX records
        show_progress (bool): Whether to show progress indicator
        
    Returns:
        Dict[str, Dict[str, Union[bool, str, Optional[str]]]]: Dictionary with validation results
    """
    results = {}
    tasks = []
    
    # Create tasks for all emails
    for email in emails:
        task = asyncio.create_task(validate_email_async(email, check_deliverability))
        tasks.append((email, task))
    
    # Process tasks with progress indicator
    total = len(tasks)
    for i, (email, task) in enumerate(tasks):
        is_valid, result, warning = await task
        results[email] = {"valid": is_valid, "result": result, "warning": warning}
        
        if show_progress:
            progress = (i + 1) / total * 100
            print(f"\rPostęp: [{i+1}/{total}] {progress:.1f}%", end="")
    
    if show_progress:
        print()  # New line after progress indicator
        
    return results

async def process_file(input_file: str, output_file: Optional[str] = None, 
                      check_deliverability: bool = True, check_existence: bool = False) -> Tuple[int, int]:
    """
    Process emails from a file and optionally write results to another file.
    
    Args:
        input_file (str): Path to file with email addresses (one per line)
        output_file (Optional[str]): Path to output file for valid emails
        check_deliverability (bool): Whether to check MX records
        check_existence (bool): Whether to check if emails actually exist
        
    Returns:
        Tuple[int, int]: (total_emails, valid_emails)
    """
    # Read emails from file
    try:
        with open(input_file, 'r') as f:
            emails = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Błąd podczas odczytu pliku: {e}")
        return 0, 0
    
    if not emails:
        print("Brak adresów email w pliku wejściowym.")
        return 0, 0
    
    print(f"Walidacja {len(emails)} adresów email...")
    start_time = time.time()
    
    # Validate all emails
    results = await batch_validate(emails, check_deliverability, check_existence)
    
    # Get valid emails with their normalized versions
    valid_emails = [(email, data["result"]) for email, data in results.items() if data["valid"]]
    
    # Write valid normalized emails to output file if specified
    if output_file and valid_emails:
        try:
            with open(output_file, 'w') as f:
                for _, normalized_email in valid_emails:
                    f.write(f"{normalized_email}\n")
            print(f"Zapisano {len(valid_emails)} poprawnych adresów do pliku {output_file}")
        except Exception as e:
            print(f"Błąd podczas zapisu do pliku: {e}")
    
    elapsed_time = time.time() - start_time
    print(f"Czas walidacji: {elapsed_time:.2f} sekund")
    print(f"Średni czas na email: {elapsed_time/len(emails):.4f} sekund")
    
    return len(emails), len(valid_emails)

async def interactive_mode():
    """
    Run the email validator in interactive mode.
    """
    print("=== Zaawansowany Walidator Emaili ===")
    print("Wprowadź adres email (lub wpisz 'exit', aby zakończyć):")
    
    # Ask if user wants to check email existence
    check_existence = input("Czy chcesz sprawdzać czy adresy email faktycznie istnieją? (tak/nie): ").lower() == 'tak'
    if check_existence:
        print("UWAGA: Sprawdzanie istnienia adresów email może być wolniejsze i mniej niezawodne.")
    
    valid_emails = []
    
    while True:
        email = input("> ").strip()
        
        if email.lower() == 'exit':
            break
        
        start_time = time.time()
        is_valid, result, warning = await validate_email_async(email, check_existence=check_existence)
        validation_time = time.time() - start_time
        
        if is_valid:
            valid_emails.append(result)
            print(f"Email '{result}' jest poprawny. (czas: {validation_time:.4f}s)")
            if warning:
                print(f"  {warning}")
        else:
            print(f"Email '{email}' jest niepoprawny. Powód: {result} (czas: {validation_time:.4f}s)")
    
    print("\nPrawidłowe adresy email:")
    if valid_emails:
        for email in valid_emails:
            print(f"- {email}")
        
        # Save valid emails to output.txt
        try:
            with open('output.txt', 'w') as f:
                for email in valid_emails:
                    f.write(f"{email}\n")
            print(f"Zapisano {len(valid_emails)} poprawnych adresów do pliku output.txt")
        except Exception as e:
            print(f"Błąd podczas zapisu do pliku: {e}")
    else:
        print("Brak prawidłowych adresów email.")

async def main_async():
    """
    Asynchronous main function with command-line argument support.
    """
    parser = argparse.ArgumentParser(description="Zaawansowany walidator adresów email")
    parser.add_argument("-f", "--file", help="Plik z adresami email (jeden na linię)")
    parser.add_argument("-o", "--output", help="Plik wyjściowy dla poprawnych adresów")
    parser.add_argument("--no-mx", action="store_true", help="Pomiń sprawdzanie rekordów MX (szybsza walidacja)")
    parser.add_argument("--email", help="Pojedynczy adres email do walidacji")
    parser.add_argument("--check-existence", action="store_true", help="Sprawdź czy adres email faktycznie istnieje")
    
    args = parser.parse_args()
    
    # Handle single email validation
    if args.email:
        start_time = time.time()
        is_valid, result, warning = await validate_email_async(args.email, not args.no_mx, args.check_existence)
        validation_time = time.time() - start_time
        
        if is_valid:
            print(f"Email '{result}' jest poprawny. (czas: {validation_time:.4f}s)")
            if warning:
                print(f"  {warning}")
        else:
            print(f"Email '{args.email}' jest niepoprawny. Powód: {result} (czas: {validation_time:.4f}s)")
        return
    
    # Handle file processing
    if args.file:
        total, valid = await process_file(args.file, args.output, not args.no_mx, args.check_existence)
        percentage = (valid/total*100) if total > 0 else 0
        print(f"Zwalidowano {total} adresów email, z czego {valid} jest poprawnych ({percentage:.1f}%)")
        if not args.check_existence:
            print("UWAGA: Walidacja sprawdza tylko czy domena może odbierać wiadomości, nie weryfikuje czy konkretny adres email istnieje.")
        return
    
    # Default to interactive mode
    await interactive_mode()

def main():
    """
    Entry point for the application.
    """
    asyncio.run(main_async())

if __name__ == "__main__":
    main()