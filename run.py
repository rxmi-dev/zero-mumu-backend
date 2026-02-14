from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import sys
import logging  # ← THIS WAS MISSING

app = Flask(__name__)

# Allow all origins for now (you can restrict later)
CORS(app, resources={r"/*": {"origins": "*"}})

# NTA 2025 Configuration
MINIMUM_WAGE = 70000 * 12  # ₦840,000 annually

def calculate_tax_2025(income):
    """NTA 2025 Progressive Tax Calculation"""
    if income <= 0:
        return 0
    
    tax = 0
    remaining = income
    
    # Band 1: First ₦800,000 @ 0%
    if remaining > 0:
        taxable = min(remaining, 800000)
        tax += taxable * 0.00
        remaining -= taxable
    
    # Band 2: Next ₦2,200,000 @ 15%
    if remaining > 0:
        taxable = min(remaining, 2200000)
        tax += taxable * 0.15
        remaining -= taxable
    
    # Band 3: Next ₦9,000,000 @ 18%
    if remaining > 0:
        taxable = min(remaining, 9000000)
        tax += taxable * 0.18
        remaining -= taxable
    
    # Band 4: Next ₦13,000,000 @ 21%
    if remaining > 0:
        taxable = min(remaining, 13000000)
        tax += taxable * 0.21
        remaining -= taxable
    
    # Band 5: Next ₦25,000,000 @ 23%
    if remaining > 0:
        taxable = min(remaining, 25000000)
        tax += taxable * 0.23
        remaining -= taxable
    
    # Band 6: Above ₦50,000,000 @ 25%
    if remaining > 0:
        tax += remaining * 0.25
    
    return round(tax, 2)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Zero Mumu Tax API',
        'version': 'NTA 2025'
    })

@app.route('/api/v1/calculate/pit', methods=['POST', 'OPTIONS'])
def calculate_pit():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print("📥 RECEIVED:", data)
        
        # Get values (default to 0 if not provided)
        gross = float(data.get('gross_income', 0))
        basic = float(data.get('basic_salary', 0))
        housing = float(data.get('housing_allowance', 0))
        transport = float(data.get('transport_allowance', 0))
        rent = float(data.get('rent_paid', 0))
        life = float(data.get('life_insurance', 0))
        paye = float(data.get('paye_deducted', 0))
        
        # Severance, Crypto, Capital Gains
        severance = float(data.get('severance_pay', 0))
        crypto = float(data.get('crypto_gains', 0))
        capital = float(data.get('capital_gains', 0))
        
        # NTA 2025 DEDUCTIONS
        pension_deduction = (basic + housing + transport) * 0.08
        nhis_deduction = basic * 0.05
        nhf_deduction = basic * 0.025
        rent_relief_calculated = rent * 0.20
        rent_relief = min(rent_relief_calculated, 500000)
        
        total_deductions = pension_deduction + nhis_deduction + nhf_deduction + rent_relief + life
        
        # TOTAL INCOME including crypto and capital gains
        total_income = gross + crypto + capital
        
        # SEVERANCE: First ₦50,000,000 exempt
        severance_taxable = max(0, severance - 50000000)
        severance_tax = calculate_tax_2025(severance_taxable) if severance_taxable > 0 else 0
        
        # Check minimum wage exemption
        if total_income <= MINIMUM_WAGE and total_income > 0:
            return jsonify({
                'success': True,
                'data': {
                    'exempt': True,
                    'minimum_wage': MINIMUM_WAGE,
                    'gross_income': total_income,
                    'message': 'Tax exempt - Minimum wage earner'
                },
                'timestamp': int(time.time())
            })
        
        # Calculate chargeable income
        chargeable = max(0, total_income - total_deductions)
        
        # Calculate tax on regular income
        regular_tax = calculate_tax_2025(chargeable)
        
        # Total tax = regular tax + severance tax
        total_tax = regular_tax + severance_tax
        
        # Calculate refund or additional tax
        if paye > total_tax:
            refund = paye - total_tax
            additional = 0
            result_type = 'refund'
        else:
            refund = 0
            additional = total_tax - paye
            result_type = 'additional' if additional > 0 else 'balanced'
        
        # Prepare response
        result = {
            'exempt': False,
            'gross_income': round(gross, 2),
            'crypto_gains': round(crypto, 2),
            'capital_gains': round(capital, 2),
            'severance_pay': round(severance, 2),
            'severance_exempt': 50000000,
            'severance_taxable': round(severance_taxable, 2),
            'severance_tax': round(severance_tax, 2),
            'total_income': round(total_income, 2),
            'basic_salary': round(basic, 2),
            'housing_allowance': round(housing, 2),
            'transport_allowance': round(transport, 2),
            'pension_deduction': round(pension_deduction, 2),
            'nhis_deduction': round(nhis_deduction, 2),
            'nhf_deduction': round(nhf_deduction, 2),
            'rent_paid': round(rent, 2),
            'rent_relief_calculated': round(rent_relief_calculated, 2),
            'rent_relief_applied': round(rent_relief, 2),
            'rent_relief_capped': rent_relief_calculated > 500000,
            'life_insurance': round(life, 2),
            'total_deductions': round(total_deductions, 2),
            'chargeable_income': round(chargeable, 2),
            'regular_tax': round(regular_tax, 2),
            'severance_tax': round(severance_tax, 2),
            'tax_payable': round(total_tax, 2),
            'paye_deducted': round(paye, 2),
            'refund_amount': round(refund, 2),
            'additional_tax': round(additional, 2),
            'result_type': result_type,
            'effective_rate': round((total_tax/total_income*100), 2) if total_income > 0 else 0
        }
        
        print("📤 SENDING:", result)
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': int(time.time())
        })
        
    except Exception as e:
        print("🔥 ERROR:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/tax-bands', methods=['GET'])
def tax_bands():
    bands = [
        {'range': '₦0 - ₦800,000', 'rate': '0%', 'tax': '₦0'},
        {'range': '₦800,001 - ₦3,000,000', 'rate': '15%', 'tax': '15% of excess'},
        {'range': '₦3,000,001 - ₦12,000,000', 'rate': '18%', 'tax': '₦330,000 + 18% of excess'},
        {'range': '₦12,000,001 - ₦25,000,000', 'rate': '21%', 'tax': '₦1,950,000 + 21% of excess'},
        {'range': '₦25,000,001 - ₦50,000,000', 'rate': '23%', 'tax': '₦4,680,000 + 23% of excess'},
        {'range': 'Above ₦50,000,000', 'rate': '25%', 'tax': '₦10,430,000 + 25% of excess'}
    ]
    return jsonify({'success': True, 'data': bands})

# This is CRITICAL for Render - MUST be at the very bottom
if __name__ != '__main__':
    # When Gunicorn imports this file, we need to ensure the app is bound
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get('PORT', 10000))
app.run(host='0.0.0.0', port=port, debug=False)
    print(f"\n{'='*60}")
    print(f"🔥 ZERO MUMU TAX BACKEND STARTING ON PORT {port}")
    print(f"{'='*60}\n")
    print(f"📍 Health check: http://0.0.0.0:{port}/health")
    print(f"📍 Tax bands: http://0.0.0.0:{port}/api/v1/tax-bands")
    print(f"{'='*60}\n")
    
    # Force stdout to flush immediately
    sys.stdout.flush()
    
    # Bind to 0.0.0.0 and the correct port
    app.run(host='0.0.0.0', port=port, debug=False)