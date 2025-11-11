def test_health_check(client):
    """Test basic health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_docs_endpoint(client):
    """Test API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_password_hashing():
    """Test password hashing works"""
    from app.security import hash_password, verify_password
    
    password = "testpass123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed) == True
    assert verify_password("wrongpass", hashed) == False

def test_otp_generation():
    """Test OTP generation"""
    from app.security import generate_otp
    
    otp = generate_otp()
    assert len(otp) == 6
    assert otp.isdigit()