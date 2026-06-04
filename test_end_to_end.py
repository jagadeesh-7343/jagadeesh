import requests
import time
import sys

BASE = "http://127.0.0.1:5000"

def wait_for_server(url, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


def register_user():
    url = BASE + "/api/register"
    payload = {
        "fullName": "E2E Test User",
        "email": "e2e_test@example.com",
        "username": "e2e_test_user",
        "password": "testpass",
        "phone": "9999999999",
        "address": "123 Test St",
        "mandal": "TestMandal",
        "district": "TestDistrict",
        "state": "TestState",
        "pincode": "500001",
        "aadhar": "111122223333"
    }
    r = requests.post(url, json=payload, timeout=10)
    print('REGISTER:', r.status_code, r.text)
    return r


def login_user():
    url = BASE + "/api/login"
    payload = {"username": "e2e_test_user", "password": "testpass"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        print('LOGIN:', r.status_code, r.text)
        return r
    except Exception as e:
        print('LOGIN ERROR:', e)
        return None


def submit_complaint():
    url = BASE + "/api/submit-complaint"
    payload = {
        "department": "education",
        "aadhaar": "111122223333",
        "phone": "9999999999",
        "address": "123 Test St",
        "mandal": "TestMandal",
        "district": "TestDistrict",
        "state": "TestState",
        "pincode": "500001",
        "problem_description": "Test complaint: streetlight not working",
        "proof_image": "",
    }
    r = requests.post(url, json=payload, timeout=10)
    print('SUBMIT_COMPLAINT:', r.status_code, r.text)
    return r


def get_complaints():
    url = BASE + "/api/complaints/education"
    r = requests.get(url, timeout=10)
    print('GET_COMPLAINTS:', r.status_code, r.text[:1000])
    return r


def track(tracking_id):
    url = BASE + f"/api/track/{tracking_id}"
    r = requests.get(url, timeout=10)
    print('TRACK:', r.status_code, r.text[:1000])
    return r


def main():
    print('Waiting for server...')
    if not wait_for_server(BASE + '/api/complaints/education', timeout=20):
        print('Server not available at', BASE)
        sys.exit(2)

    r = register_user()
    try:
        if r.status_code in (200, 201):
            data = r.json()
            assert 'citizen_id' in data, f"No citizen_id in register response: {data}"
            citizen_id = data['citizen_id']
            print('Registered citizen_id:', citizen_id)
        else:
            # If user already exists, try logging in to get citizen id
            print('Register returned', r.status_code, 'trying to login instead')
            lr = login_user()
            assert lr is not None and lr.status_code == 200, f"Login failed after register error: {lr}"
            ld = lr.json()
            citizen_id = ld['user']['id']
            print('Logged in citizen_id:', citizen_id)
    except Exception as e:
        print('REGISTER ASSERTION FAILED:', e)
        sys.exit(1)

    r2 = submit_complaint()
    try:
        assert r2.status_code == 201, f"Submit complaint failed: {r2.status_code} {r2.text}"
        data2 = r2.json()
        tracking = data2.get('tracking_id')
        assert tracking, f"No tracking_id in submit response: {data2}"
        print('Tracking ID:', tracking)
    except Exception as e:
        print('SUBMIT ASSERTION FAILED:', e)
        sys.exit(1)

    try:
        tr = track(tracking)
        assert tr.status_code == 200, f"Track endpoint failed: {tr.status_code} {tr.text}"
    except Exception as e:
        print('TRACK ASSERTION FAILED:', e)
        sys.exit(1)

    g = get_complaints()
    try:
        assert g.status_code == 200, f"Get complaints failed: {g.status_code} {g.text}"
        arr = g.json()
        assert any((c.get('tracking_id') == tracking) for c in arr), 'Submitted complaint not found in list'
        print('E2E test passed')
        sys.exit(0)
    except Exception as e:
        print('GET_COMPLAINTS ASSERTION FAILED:', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
