from sim_utils import is_number_valid
from cnic_utils import validate_cnic

def test_number_validation():
    print("Testing Number Validation...")
    valid_numbers = ["03001234567", "923001234567"]
    invalid_numbers = ["123", "0300123456", "92300123456", "abc", "0300-1234567"]
    
    for num in valid_numbers:
        assert is_number_valid(num) is True, f"Failed for valid number: {num}"
    
    for num in invalid_numbers:
        assert is_number_valid(num) is False, f"Failed for invalid number: {num}"
    print("[PASS] Number validation works correctly.")

def test_cnic_validation():
    print("\nTesting CNIC Validation...")
    valid_cnics = ["12345-1234567-1", "1234512345671"]
    invalid_cnics = ["12345-1234567-", "123451234567", "12345-123456-1", "abc"]
    
    for cnic in valid_cnics:
        assert validate_cnic(cnic) is True, f"Failed for valid CNIC: {cnic}"
    
    for cnic in invalid_cnics:
        assert validate_cnic(cnic) is False, f"Failed for invalid CNIC: {cnic}"
    print("[PASS] CNIC validation works correctly.")

if __name__ == "__main__":
    try:
        test_number_validation()
        test_cnic_validation()
        print("\nAll logic tests passed successfully!")
    except AssertionError as e:
        print(f"\n[FAIL] {e}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
