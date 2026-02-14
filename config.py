import os

class Config:
    SECRET_KEY = 'dev-key-123'
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000', 'http://127.0.0.1:5173']
    
    # NTA 2025 - CORRECT
    MINIMUM_WAGE = 70000 * 12  # ₦840,000
    
    PIT_TAX_BANDS = [
        {"limit": 800000, "rate": 0.00},
        {"limit": 3000000, "rate": 0.15},
        {"limit": 12000000, "rate": 0.18},
        {"limit": 25000000, "rate": 0.21},
        {"limit": 50000000, "rate": 0.23},
        {"limit": None, "rate": 0.25}
    ]