import asyncio
import re
import time
import os
import argparse
import smtplib
import json
from email_validator import validate_email, EmailNotValidError
from validate_email import validate_email as verify_email_exists
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple, Set, Optional, Union
from collections import defaultdict

# Regular expression for basic email validation
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Cache for domain validation results
domain_cache: Dict[str, bool] = {}

# Cache for email existence results
email_existence_cache: Dict[str, bool] = {}

# Cache file path
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'email_cache.json')

# Default settings
DEFAULT_BATCH_SIZE = 50
DEFAULT_MAX_WORKERS = 20
DEFAULT_SMTP_TIMEOUT = 5
DEFAULT_MAX_CONCURRENT_DOMAINS = 10

def load_cache():
    """Load domain and email existence cache from disk if available"""
    global domain_cache, email_existence_cache
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                domain_cache = cache_data.get('domains', {})
                email_existence_cache = cache_data.get('emails', {})
                print(f"Załadowano {len(domain_cache)} domen i {len(email_existence_cache)} adresów email z pamięci podręcznej")
    except Exception as e:
        print(f"Błąd podczas ładowania pamięci podręcznej: {str(e)}")

def save_cache():
    """Save domain and email existence cache to disk"""
    try:
        cache_data = {
            'domains': domain_cache,
            'emails': email_existence_cache
        }
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
        print(f"Zapisano {len(domain_cache)} domen i {len(email_existence_cache)} adresów email do pamięci podręcznej")
    except Exception as e:
        print(f"Błąd podczas zapisywania pamięci podręcznej: {str(e)}")

def quick_validate(email: str) -> bool:
    """
    Quickly validate email format using regex before more expensive checks.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if the email passes basic format validation
    """
    return bool(EMAIL_REGEX.match(email))

async def check_email_exists(email: str, timeout: int = DEFAULT_SMTP_TIMEOUT) -> Tuple[bool, Optional[str]]:
    """
    Check if an email address actually exists by verifying with the mail server.
    
    Args:
        email (str): The email address to check
        timeout (int): SMTP timeout in seconds
        
    Returns:
        tuple: (exists, error_message) where:
            - exists (bool): True if email exists, False otherwise
            - error_message (Optional[str]): Error message if applicable
    """
    # Check cache first
    if email in email_existence_cache:
        exists = email_existence_cache[email]
        return exists, None if exists else "Adres email nie istnieje na serwerze pocztowym (z pamięci podręcznej)"
    
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
                    smtp_timeout=timeout,  # Configurable timeout
                    smtp_helo_host='my.host.name',  # HELO hostname
                    smtp_from_address='verify@example.com',  # MAIL FROM address
                    smtp_skip_tls=False, # Don't skip TLS
                    smtp_tls_context=None, # Use default TLS context
                    smtp_debug=False     # Don't show debug info
                )
            )
        
        # Update cache
        email_existence_cache[email] = exists
        
        if exists:
            return True, None
        else:
            return False, "Adres email nie istnieje na serwerze pocztowym"
    except Exception as e:
        return False, f"Błąd podczas weryfikacji istnienia adresu email: {str(e)}"

async def check_email_exists_batch(emails_by_domain: Dict[str, List[str]], 
                                  timeout: int = DEFAULT_SMTP_TIMEOUT) -> Dict[str, Tuple[bool, Optional[str]]]:
    """
    Check if multiple email addresses with the same domain exist by verifying with the mail server.
    Processes emails in batches grouped by domain to reuse SMTP connections.
    
    Args:
        emails_by_domain (Dict[str, List[str]]): Dictionary mapping domains to lists of emails
        timeout (int): SMTP timeout in seconds
        
    Returns:
        Dict[str, Tuple[bool, Optional[str]]]: Dictionary mapping emails to (exists, error_message) tuples
    """
    results = {}
    
    # Process each domain in parallel with a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(DEFAULT_MAX_CONCURRENT_DOMAINS)
    tasks = []
    
    for domain, emails in emails_by_domain.items():
        task = asyncio.create_task(check_domain_emails(domain, emails, semaphore, timeout))
        tasks.append(task)
    
    # Wait for all domain tasks to complete
    domain_results = await asyncio.gather(*tasks)
    
    # Combine results from all domains
    for domain_result in domain_results:
        results.update(domain_result)
    
    return results

async def check_domain_emails(domain: str, emails: List[str], 
                             semaphore: asyncio.Semaphore, 
                             timeout: int) -> Dict[str, Tuple[bool, Optional[str]]]:
    """
    Check all emails for a specific domain using a single SMTP connection if possible.
    
    Args:
        domain (str): The domain to check
        emails (List[str]): List of emails with this domain
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent connections
        timeout (int): SMTP timeout in seconds
        
    Returns:
        Dict[str, Tuple[bool, Optional[str]]]: Results for all emails in this domain
    """
    results = {}
    
    # Check cache first for all emails
    unchecked_emails = []
    for email in emails:
        if email in email_existence_cache:
            exists = email_existence_cache[email]
            results[email] = (exists, None if exists else "Adres email nie istnieje na serwerze pocztowym (z pamięci podręcznej)")
        else:
            unchecked_emails.append(email)
    
    if not unchecked_emails:
        return results
    
    # Use semaphore to limit concurrent connections
    async with semaphore:
        try:
            # Run the CPU-bound validation in a thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=DEFAULT_MAX_WORKERS) as pool:
                # Process emails in smaller batches to avoid overwhelming the server
                for i in range(0, len(unchecked_emails), DEFAULT_BATCH_SIZE):
                    batch = unchecked_emails[i:i+DEFAULT_BATCH_SIZE]
                    batch_results = await asyncio.gather(
                        *[loop.run_in_executor(
                            pool,
                            lambda e=email: (
                                e,
                                verify_email_exists(
                                    e,
                                    check_format=False,
                                    check_dns=False,
                                    check_smtp=True,
                                    smtp_timeout=timeout,
                                    smtp_helo_host='my.host.name',
                                    smtp_from_address='verify@example.com',
                                    smtp_skip_tls=False,
                                    smtp_tls_context=None,
                                    smtp_debug=False
                                )
                            )
                        ) for email in batch]
                    )
                    
                    for email, exists in batch_results:
                        # Update cache
                        email_existence_cache[email] = exists
                        results[email] = (exists, None if exists else "Adres email nie istnieje na serwerze pocztowym")
        except Exception as e:
            # If there's an error with the domain, mark all remaining emails as failed
            error_msg = f"Błąd podczas weryfikacji istnienia adresów email dla domeny {domain}: {str(e)}"
            for email in unchecked_emails:
                if email not in results:
                    results[email] = (False, error_msg)
    
    return results

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
        
        # If check_existence is True, verify if the email actually exists
        if check_existence:
            exists, error_message = await check_email_exists(email, timeout)
            if not exists:
                return False, error_message or "Adres email nie istnieje na serwerze pocztowym", None
            # No warning needed if we've verified existence
            return True, valid.normalized, None
        else:
            # Only show warning if we didn't check existence
            warning = "UWAGA: Walidacja sprawdza tylko czy domena może odbierać wiadomości, nie weryfikuje czy konkretny adres email istnieje."
            return True, valid.normalized, warning
    except EmailNotValidError as e:
        # Cache the negative result
        if check_deliverability and domain not in domain_cache:
            domain_cache[domain] = False
        return False, str(e), None

async def batch_validate(emails: List[str], check_deliverability: bool = True, 
                         check_existence: bool = False, show_progress: bool = True) -> Dict[str, Dict[str, Union[bool, str, Optional[str]]]]:
    """
    Validate multiple email addresses concurrently with optimized batching.
    
    Args:
        emails (List[str]): List of email addresses to validate
        check_deliverability (bool): Whether to check MX records
        check_existence (bool): Whether to check if emails actually exist
        show_progress (bool): Whether to show progress indicator
        
    Returns:
        Dict[str, Dict[str, Union[bool, str, Optional[str]]]]: Dictionary with validation results
    """
    results = {}
    total = len(emails)
    processed = 0
    start_time = time.time()
    
    # First pass: quick validation and domain grouping
    valid_emails = []
    invalid_emails = []
    emails_by_domain = defaultdict(list)
    
    for email in emails:
        if not quick_validate(email):
            results[email] = {
                "valid": False, 
                "result": "Niepoprawny format adresu email", 
                "warning": None
            }
            invalid_emails.append(email)
        else:
            valid_emails.append(email)
            try:
                domain = email.split('@')[1]
                emails_by_domain[domain].append(email)
            except IndexError:
                results[email] = {
                    "valid": False, 
                    "result": "Brak znaku @ w adresie email", 
                    "warning": None
                }
                invalid_emails.append(email)
    
    processed += len(invalid_emails)
    if show_progress and processed > 0:
        progress = processed / total * 100
        elapsed = time.time() - start_time
        emails_per_second = processed / elapsed if elapsed > 0 else 0
        remaining = (total - processed) / emails_per_second if emails_per_second > 0 else 0
        print(f"\rPostęp: [{processed}/{total}] {progress:.1f}% | {emails_per_second:.1f} email/s | Pozostało: {remaining:.1f}s", end="")
    
    # Create tasks for all valid emails
    tasks = []
    for email in valid_emails:
        task = asyncio.create_task(validate_email_async(email, check_deliverability, False))
        tasks.append((email, task))
    
    # Process tasks with progress indicator
    for i, (email, task) in enumerate(tasks):
        is_valid, result, warning = await task
        results[email] = {"valid": is_valid, "result": result, "warning": warning}
        
        processed += 1
        if show_progress and i % 10 == 0:  # Update progress every 10 emails
            progress = processed / total * 100
            elapsed = time.time() - start_time
            emails_per_second = processed / elapsed if elapsed > 0 else 0
            remaining = (total - processed) / emails_per_second if emails_per_second > 0 else 0
            print(f"\rPostęp: [{processed}/{total}] {progress:.1f}% | {emails_per_second:.1f} email/s | Pozostało: {remaining:.1f}s", end="")
    
    # If we need to check existence, do it efficiently by domain
    if check_existence:
        # Filter out emails that already failed validation
        for domain, domain_emails in list(emails_by_domain.items()):
            emails_by_domain[domain] = [e for e in domain_emails if e in valid_emails and (e not in results or results[e]["valid"])]
            if not emails_by_domain[domain]:
                del emails_by_domain[domain]
        
        # Check existence for all remaining emails by domain
        if emails_by_domain:
            existence_results = await check_email_exists_batch(emails_by_domain, DEFAULT_SMTP_TIMEOUT)
            
            # Update results with existence check
            for email, (exists, error_message) in existence_results.items():
                if email in results and results[email]["valid"]:
                    if exists:
                        # Keep the existing result but remove warning
                        results[email]["warning"] = None
                    else:
                        # Update to invalid with error message
                        results[email] = {
                            "valid": False,
                            "result": error_message or "Adres email nie istnieje na serwerze pocztowym",
                            "warning": None
                        }
    
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
    # Load cache at the beginning
    load_cache()
    
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
    
    # Validate all emails with optimized batch processing
    results = await batch_validate(emails, check_deliverability, check_existence, True)
    
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
    print(f"Prędkość: {len(emails)/elapsed_time:.1f} email/s")
    
    # Save cache at the end
    save_cache()
    
    return len(emails), len(valid_emails)

async def interactive_mode():
    """
    Run the email validator in interactive mode.
    """
    # Load cache at the beginning
    load_cache()
    
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
    
    # Save cache at the end
    save_cache()

async def main_async():
    """
    Asynchronous main function with command-line argument support.
    """
    # Global declaration at the top of the function
    global DEFAULT_BATCH_SIZE, DEFAULT_MAX_WORKERS, DEFAULT_SMTP_TIMEOUT, DEFAULT_MAX_CONCURRENT_DOMAINS
    
    parser = argparse.ArgumentParser(description="Zaawansowany walidator adresów email")
    parser.add_argument("-f", "--file", help="Plik z adresami email (jeden na linię)")
    parser.add_argument("-o", "--output", help="Plik wyjściowy dla poprawnych adresów")
    parser.add_argument("--no-mx", action="store_true", help="Pomiń sprawdzanie rekordów MX (szybsza walidacja)")
    parser.add_argument("--email", help="Pojedynczy adres email do walidacji")
    parser.add_argument("--check-existence", action="store_true", help="Sprawdź czy adres email faktycznie istnieje")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help=f"Rozmiar partii dla przetwarzania (domyślnie: {DEFAULT_BATCH_SIZE})")
    parser.add_argument("--timeout", type=int, default=DEFAULT_SMTP_TIMEOUT, help=f"Timeout dla połączeń SMTP w sekundach (domyślnie: {DEFAULT_SMTP_TIMEOUT})")
    parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS, help=f"Maksymalna liczba wątków (domyślnie: {DEFAULT_MAX_WORKERS})")
    parser.add_argument("--max-domains", type=int, default=DEFAULT_MAX_CONCURRENT_DOMAINS, help=f"Maksymalna liczba jednoczesnych domen (domyślnie: {DEFAULT_MAX_CONCURRENT_DOMAINS})")
    
    args = parser.parse_args()
    
    # Update global settings if provided
    if args.batch_size:
        DEFAULT_BATCH_SIZE = args.batch_size
    if args.max_workers:
        DEFAULT_MAX_WORKERS = args.max_workers
    if args.timeout:
        DEFAULT_SMTP_TIMEOUT = args.timeout
    if args.max_domains:
        DEFAULT_MAX_CONCURRENT_DOMAINS = args.max_domains
    
    # Load cache at the beginning
    load_cache()
    
    # Handle single email validation
    if args.email:
        start_time = time.time()
        is_valid, result, warning = await validate_email_async(args.email, not args.no_mx, args.check_existence, DEFAULT_SMTP_TIMEOUT)
        validation_time = time.time() - start_time
        
        if is_valid:
            print(f"Email '{result}' jest poprawny. (czas: {validation_time:.4f}s)")
            if warning:
                print(f"  {warning}")
        else:
            print(f"Email '{args.email}' jest niepoprawny. Powód: {result} (czas: {validation_time:.4f}s)")
        
        # Save cache before exit
        save_cache()
        return
    
    # Handle file processing
    if args.file:
        total, valid = await process_file(args.file, args.output, not args.no_mx, args.check_existence)
        percentage = (valid/total*100) if total > 0 else 0
        print(f"Zwalidowano {total} adresów email, z czego {valid} jest poprawnych ({percentage:.1f}%)")
        if not args.check_existence:
            print("UWAGA: Walidacja sprawdza tylko czy domena może odbierać wiadomości, nie weryfikuje czy konkretny adres email istnieje.")
        
        # Save cache before exit
        save_cache()
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