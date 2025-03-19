from email_validator import validate_email, EmailNotValidError

def validate_email_address(email):
    """
    Validates an email address for syntax and deliverability.
    
    Args:
        email (str): The email address to validate
        
    Returns:
        tuple: (is_valid, result) where:
            - is_valid (bool): True if email is valid, False otherwise
            - result (str): Normalized email if valid, error message if invalid
    """
    try:
        valid = validate_email(email, check_deliverability=True)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)

def main():
    """
    Main function that runs the email validator program.
    """
    print("=== Walidator emaili ===")
    print("Wprowadź adres email (lub wpisz 'exit', aby zakończyć):")
    valid_emails = []
    
    while True:
        email = input("> ").strip()
        
        if email.lower() == 'exit':
            break
        
        is_valid, result = validate_email_address(email)
        
        if is_valid:
            valid_emails.append(result)
            print(f"Email '{result}' jest poprawny.")
        else:
            print(f"Email '{email}' jest niepoprawny. Powód: {result}")
    
    print("\nPrawidłowe adresy email:")
    if valid_emails:
        for email in valid_emails:
            print(f"- {email}")
    else:
        print("Brak prawidłowych adresów email.")

if __name__ == "__main__":
    main()