import asyncio
import re
import time
import os
import argparse
from email_validator import validate_email, EmailNotValidError
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

async def validate_email_async(email: str, check_deliverability: bool = True) -> Tuple[bool, str]:
    """
    Asynchronously validate an email address.
    
    Args:
        email (str): The email address to validate
        check_deliverability (bool): Whether to check MX records
        
    Returns:
        tuple: (is_valid, result) where:
            - is_valid (bool): True if email is valid, False otherwise
            - result (str): Normalized email if valid, error message if invalid
    """
    # Quick validation first
    if not quick_validate(email):
        return False, "Niepoprawny format adresu email"
    
    # Extract domain for cache lookup
    try:
        domain = email.split('@')[1]
    except IndexError:
        return False, "Brak znaku @ w adresie email"
    
    # Check cache for domain validation result
    if check_deliverability and domain in domain_cache:
        if not domain_cache[domain]:
            return False, f"Domena {domain} nie może odbierać wiadomości (z pamięci podręcznej)"
    
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
            
        return True, valid.email
    except EmailNotValidError as e:
        # Cache the negative result
        if check_deliverability and domain not in domain_cache:
            domain_cache[domain] = False
        return False, str(e)

async def batch_validate(emails: List[str], check_deliverability: bool = True, 
                         show_progress: bool = True) -> Dict[str, Union[str, bool]]:
    """
    Validate multiple email addresses concurrently.
    
    Args:
        emails (List[str]): List of email addresses to validate
        check_deliverability (bool): Whether to check MX records
        show_progress (bool): Whether to show progress indicator
        
    Returns:
        Dict[str, Union[str, bool]]: Dictionary with validation results
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
        is_valid, result = await task
        results[email] = {"valid": is_valid, "result": result}
        
        if show_progress:
            progress = (i + 1) / total * 100
            print(f"\rPostęp: [{i+1}/{total}] {progress:.1f}%", end="")
    
    if show_progress:
        print()  # New line after progress indicator
        
    return results

async def process_file(input_file: str, output_file: Optional[str] = None, 
                      check_deliverability: bool = True) -> Tuple[int, int]:
    """
    Process emails from a file and optionally write results to another file.
    
    Args:
        input_file (str): Path to file with email addresses (one per line)
        output_file (Optional[str]): Path to output file for valid emails
        check_deliverability (bool): Whether to check MX records
        
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
    results = await batch_validate(emails, check_deliverability)
    
    # Count valid emails
    valid_emails = [email for email, data in results.items() if data["valid"]]
    
    # Write valid emails to output file if specified
    if output_file and valid_emails:
        try:
            with open(output_file, 'w') as f:
                for email in valid_emails:
                    f.write(f"{email}\n")
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
    valid_emails = []
    
    while True:
        email = input("> ").strip()
        
        if email.lower() == 'exit':
            break
        
        start_time = time.time()
        is_valid, result = await validate_email_async(email)
        validation_time = time.time() - start_time
        
        if is_valid:
            valid_emails.append(result)
            print(f"Email '{result}' jest poprawny. (czas: {validation_time:.4f}s)")
        else:
            print(f"Email '{email}' jest niepoprawny. Powód: {result} (czas: {validation_time:.4f}s)")
    
    print("\nPrawidłowe adresy email:")
    if valid_emails:
        for email in valid_emails:
            print(f"- {email}")
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
    
    args = parser.parse_args()
    
    # Handle single email validation
    if args.email:
        start_time = time.time()
        is_valid, result = await validate_email_async(args.email, not args.no_mx)
        validation_time = time.time() - start_time
        
        if is_valid:
            print(f"Email '{result}' jest poprawny. (czas: {validation_time:.4f}s)")
        else:
            print(f"Email '{args.email}' jest niepoprawny. Powód: {result} (czas: {validation_time:.4f}s)")
        return
    
    # Handle file processing
    if args.file:
        total, valid = await process_file(args.file, args.output, not args.no_mx)
        percentage = (valid/total*100) if total > 0 else 0
        print(f"Zwalidowano {total} adresów email, z czego {valid} jest poprawnych ({percentage:.1f}%)")
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