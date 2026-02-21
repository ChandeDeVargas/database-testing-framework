"""
Email Validation Tests
Detect invalid, malformed, or suspicious email addresses

Email quality issues cause:
- Bounced marketing emails (wasted budget)
- Failed account verification
- Customer support tickets
- Fraud/fake accounts
"""
import pytest
import re
from config.models import User


class TestEmailValidation:
    """
    Validate email format and quality.
    
    Business Impact:
    - Invalid emails = can't contact customers
    - Fake emails = fraud risk
    - Malformed emails = system errors
    """
    
    def test_email_contains_at_symbol(self, db_session, sample_users):
        """
        Test: All emails contain @ symbol
        
        Most basic email validation
        Common error: Copy/paste without @
        """
        invalid_emails = []
        
        for user in sample_users:
            if '@' not in user.email:
                invalid_emails.append({
                    'user_id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'issue': 'Missing @ symbol'
                })
        
        if invalid_emails:
            print(f"\nCRITICAL: Found {len(invalid_emails)} emails without @ symbol!")
            for item in invalid_emails:
                print(f"   User {item['user_id']} ({item['name']}): '{item['email']}'")
        
        assert len(invalid_emails) == 0, \
            f"DATA QUALITY: {len(invalid_emails)} invalid emails (no @ symbol)"
        
        print(f"\nEmail Format: All {len(sample_users)} emails contain @")
    
    
    def test_email_has_domain(self, db_session, sample_users):
        """
        Test: All emails have a domain after @
        
        Valid: user@example.com
        Invalid: user@, @example.com, user@@example.com
        """
        invalid_emails = []
        
        for user in sample_users:
            email = user.email
            
            # Check if there's text after @
            if '@' in email:
                parts = email.split('@')
                if len(parts) != 2 or not parts[1] or not parts[0]:
                    invalid_emails.append({
                        'user_id': user.id,
                        'email': email,
                        'issue': 'Malformed @ structure'
                    })
                elif '.' not in parts[1]:
                    invalid_emails.append({
                        'user_id': user.id,
                        'email': email,
                        'issue': 'Domain missing . (dot)'
                    })
        
        if invalid_emails:
            print(f"\nCRITICAL: Found {len(invalid_emails)} malformed email domains!")
            for item in invalid_emails:
                print(f"   User {item['user_id']}: '{item['email']}' - {item['issue']}")
        
        assert len(invalid_emails) == 0, \
            f"DATA QUALITY: {len(invalid_emails)} emails with invalid domains"
        
        print(f"\nEmail Domains: All emails have valid domain structure")
    
    
    def test_email_no_whitespace(self, db_session, sample_users):
        """
        Test: Emails don't contain whitespace
        
        Common error: Copy/paste with trailing spaces
        " user@example.com" vs "user@example.com"
        """
        invalid_emails = []
        
        for user in sample_users:
            email = user.email
            
            if email != email.strip():
                invalid_emails.append({
                    'user_id': user.id,
                    'email': repr(email),  # Shows spaces
                    'issue': 'Leading/trailing whitespace'
                })
            
            if ' ' in email:
                invalid_emails.append({
                    'user_id': user.id,
                    'email': email,
                    'issue': 'Contains spaces'
                })
        
        if invalid_emails:
            print(f"\nCRITICAL: Found {len(invalid_emails)} emails with whitespace!")
            for item in invalid_emails:
                print(f"   User {item['user_id']}: {item['email']} - {item['issue']}")
        
        assert len(invalid_emails) == 0, \
            f"DATA QUALITY: {len(invalid_emails)} emails with whitespace"
        
        print(f"\nEmail Whitespace: No emails contain spaces")
    
    
    def test_email_regex_pattern(self, db_session, sample_users):
        """
        Test: Emails match standard RFC-compliant pattern
        
        Pattern: local@domain.tld
        - local: alphanumeric + some special chars
        - domain: alphanumeric + hyphens
        - tld: 2-6 letters
        """
        # Simplified RFC 5322 pattern
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        invalid_emails = []
        
        for user in sample_users:
            email = user.email
            
            if not email_pattern.match(email):
                invalid_emails.append({
                    'user_id': user.id,
                    'email': email,
                    'issue': 'Does not match RFC pattern'
                })
        
        if invalid_emails:
            print(f"\nWARNING: Found {len(invalid_emails)} non-RFC compliant emails!")
            for item in invalid_emails:
                print(f"   User {item['user_id']}: '{item['email']}'")
        
        assert len(invalid_emails) == 0, \
            f"DATA QUALITY: {len(invalid_emails)} emails don't match RFC pattern"
        
        print(f"\nEmail Pattern: All emails are RFC-compliant")
    
    
    def test_email_suspicious_patterns(self, db_session, sample_users):
        """
        Test: Detect suspicious/fake email patterns
        
        Patterns that indicate fake accounts:
        - test@test.com
        - admin@admin.com
        - Multiple consecutive numbers (user12345@...)
        - Disposable email domains
        """
        suspicious_patterns = [
            r'test@test',
            r'admin@admin',
            r'fake@',
            r'noreply@',
            r'@mailinator',  # Disposable email service
            r'@guerrillamail',
            r'@10minutemail',
            r'\d{5,}@',  # 5+ consecutive digits in local part
        ]
        
        suspicious_emails = []
        
        for user in sample_users:
            email = user.email.lower()
            
            for pattern in suspicious_patterns:
                if re.search(pattern, email):
                    suspicious_emails.append({
                        'user_id': user.id,
                        'email': user.email,
                        'pattern': pattern,
                        'risk': 'Potential fake/test account'
                    })
                    break
        
        if suspicious_emails:
            print(f"\nWARNING: Found {len(suspicious_emails)} suspicious emails!")
            for item in suspicious_emails:
                print(f"   User {item['user_id']}: {item['email']} "
                      f"(pattern: {item['pattern']})")
        
        # This is a warning, not a hard failure
        # (legitimate users might have "test" in their name)
        if len(suspicious_emails) > len(sample_users) * 0.1:  # >10% suspicious
            pytest.fail(
                f"DATA QUALITY: {len(suspicious_emails)} suspicious emails "
                f"({len(suspicious_emails)/len(sample_users)*100:.1f}%)"
            )
        
        print(f"\nEmail Patterns: Suspicious email rate acceptable")
    
    
    def test_email_case_consistency(self, db_session):
        """
        Test: Detect case-sensitivity issues
        
        Problem: user@Example.com vs user@example.com
        Email addresses are case-insensitive but often stored inconsistently
        
        Business Impact:
        - Duplicate accounts
        - Login issues
        - Broken uniqueness constraints
        """
        # Get all emails
        all_users = db_session.query(User).all()
        
        # Group by lowercase email
        email_groups = {}
        for user in all_users:
            email_lower = user.email.lower()
            if email_lower not in email_groups:
                email_groups[email_lower] = []
            email_groups[email_lower].append({
                'id': user.id,
                'original': user.email
            })
        
        # Find case variations
        case_issues = {}
        for email_lower, users in email_groups.items():
            # Get unique case variations
            variations = set(u['original'] for u in users)
            if len(variations) > 1:
                case_issues[email_lower] = list(variations)
        
        if case_issues:
            print(f"\nWARNING: Found {len(case_issues)} emails with case variations!")
            for email_lower, variations in case_issues.items():
                print(f"   Base: {email_lower}")
                print(f"   Variations: {variations}")
        
        assert len(case_issues) == 0, \
            f"DATA QUALITY: {len(case_issues)} emails have case inconsistencies"
        
        print(f"\nEmail Case: All emails have consistent casing")