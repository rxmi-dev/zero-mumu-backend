"""
NTA 2025 CORRECTED API Endpoints
"""
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
import time
from app.core.calculations import TaxCalculator
from flask_cors import cross_origin

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Zero Mumu Tax API - NTA 2025',
        'version': '1.0.0',
        'year': '2026'
    })

@api_bp.route('/api/v1/calculate/pit', methods=['POST', 'OPTIONS'])
@cross_origin(origins='*')
def calculate_pit():
    """NTA 2025 CORRECTED PIT Calculator"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        request_data = request.get_json()
        print("=== REQUEST RECEIVED ===")
        print("Data:", request_data)
        
        if not request_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Default values for missing fields
        defaults = {
            'gross_income': 0,
            'basic_salary': 0,
            'housing_allowance': 0,
            'transport_allowance': 0,
            'rent_paid': 0,
            'life_insurance': 0,
            'mortgage_interest': 0,
            'paye_deducted': 0,
            'crypto_gains': 0,
            'capital_gains': 0,
            'severance_pay': 0
        }
        
        for key, default in defaults.items():
            if key not in request_data:
                request_data[key] = default
        
        result = TaxCalculator.calculate_pit(request_data)
        print("=== CALCULATION RESULT ===")
        print(result)
        
        response = {
            'success': True,
            'data': result,
            'timestamp': int(time.time()),
            'compliance': 'NTA 2025'
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print("=== ERROR ===")
        print(str(e))
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': 'Calculation failed',
            'message': str(e)
        }), 500

@api_bp.route('/api/v1/calculate/vat', methods=['POST'])
@cross_origin()
def calculate_vat():
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = TaxCalculator.calculate_vat(request_data)
        
        response = {
            'success': True,
            'data': result,
            'timestamp': int(time.time())
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Calculation failed',
            'message': 'An error occurred'
        }), 500

@api_bp.route('/api/v1/calculate/rent-relief', methods=['POST'])
@cross_origin()
def calculate_rent_relief():
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = TaxCalculator.calculate_rent_relief(request_data)
        
        response = {
            'success': True,
            'data': result,
            'timestamp': int(time.time())
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Calculation failed',
            'message': 'An error occurred'
        }), 500

@api_bp.route('/api/v1/tax-bands', methods=['GET'])
@cross_origin()
def get_tax_bands():
    """Get NTA 2025 Tax Bands"""
    bands = current_app.config['PIT_TAX_BANDS']
    
    formatted_bands = []
    prev_limit = 0
    
    for band in bands:
        if band["limit"]:
            range_text = f"₦{prev_limit:,.0f} - ₦{band['limit']:,.0f}"
            amount_in_band = band["limit"] - prev_limit
        else:
            range_text = f"Above ₦{prev_limit:,.0f}"
            amount_in_band = "Unlimited"
        
        formatted_bands.append({
            'range': range_text,
            'amount_in_band': amount_in_band,
            'rate': band['rate'] * 100,
            'rate_display': f"{band['rate'] * 100:.0f}%"
        })
        prev_limit = band["limit"] if band["limit"] else prev_limit
    
    return jsonify({
        'success': True,
        'data': formatted_bands,
        'year': '2025',
        'effective_date': 'January 1, 2026',
        'minimum_wage': current_app.config['MINIMUM_WAGE']
    }), 200