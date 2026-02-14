"""
NTA 2025 CORRECTED Tax Calculations
All deductions calculated BEFORE tax, per NTA 2025
"""
from flask import current_app

class TaxCalculator:
    @staticmethod
    def calculate_progressive_tax(income, tax_bands):
        """Calculate tax using progressive bands"""
        if income <= 0:
            return 0
        
        tax = 0
        previous_limit = 0
        
        for band in tax_bands:
            if income > previous_limit:
                if band["limit"]:
                    taxable_in_band = min(income - previous_limit, band["limit"] - previous_limit)
                else:
                    taxable_in_band = income - previous_limit
                
                tax += taxable_in_band * band["rate"]
                previous_limit = band["limit"] if band["limit"] else income
        
        return round(tax, 2)
    
    @staticmethod
    def calculate_pit(data):
        """Calculate Personal Income Tax - NTA 2025 CORRECTED"""
        try:
            # NTA 2025: Get income components
            gross_income = float(data.get('gross_income', 0))
            crypto_gains = float(data.get('crypto_gains', 0))
            capital_gains = float(data.get('capital_gains', 0))
            severance = float(data.get('severance_pay', 0))
            
            # NTA 2025: Get salary components for auto-calculation
            basic_salary = float(data.get('basic_salary', 0))
            housing_allowance = float(data.get('housing_allowance', 0))
            transport_allowance = float(data.get('transport_allowance', 0))
            
            # NTA 2025: Other deductions
            rent_paid = float(data.get('rent_paid', 0))
            life_insurance = float(data.get('life_insurance', 0))
            mortgage_interest = float(data.get('mortgage_interest', 0))
            paye_deducted = float(data.get('paye_deducted', 0))
            
            # === NTA 2025 AUTO-CALCULATED DEDUCTIONS ===
            # Pension: 8% of (Basic + Housing + Transport)
            pension_deduction = (basic_salary + housing_allowance + transport_allowance) * 0.08
            
            # NHIS: 5% of Basic Salary
            nhis_deduction = basic_salary * 0.05
            
            # NHF: 2.5% of Basic Salary
            nhf_deduction = basic_salary * 0.025
            
            # Rent Relief: 20% of rent, max ₦500,000
            rent_relief = min(rent_paid * 0.20, 500000)
            
            # === NTA 2025 TOTAL INCOME (includes crypto/capital gains) ===
            total_gross_income = gross_income + crypto_gains + capital_gains
            
            # Check minimum wage exemption
            if total_gross_income <= current_app.config['MINIMUM_WAGE']:
                return {
                    'exempt': True,
                    'minimum_wage': current_app.config['MINIMUM_WAGE'],
                    'gross_income': total_gross_income,
                    'message': 'Tax exempt - Minimum wage earner'
                }
            
            # === NTA 2025 TOTAL DEDUCTIONS ===
            total_deductions = (
                pension_deduction +
                nhis_deduction +
                nhf_deduction +
                rent_relief +
                life_insurance +
                mortgage_interest
            )
            
            # === NTA 2025 CHARGEABLE INCOME ===
            chargeable_income = max(0, total_gross_income - total_deductions)
            
            # === NTA 2025 PROGRESSIVE TAX ===
            tax_payable = TaxCalculator.calculate_progressive_tax(
                chargeable_income, 
                current_app.config['PIT_TAX_BANDS']
            )
            
            # === NTA 2025 SEVERANCE EXEMPTION (first ₦50m) ===
            severance_tax = 0
            if severance > 0:
                taxable_severance = max(0, severance - 50000000)  # ₦50m exemption
                severance_tax = TaxCalculator.calculate_progressive_tax(
                    taxable_severance, 
                    current_app.config['PIT_TAX_BANDS']
                )
            
            total_tax_payable = tax_payable + severance_tax
            
            # Determine refund or additional tax
            if paye_deducted > total_tax_payable:
                refund_amount = paye_deducted - total_tax_payable
                additional_tax = 0
                result_type = 'refund'
            else:
                refund_amount = 0
                additional_tax = total_tax_payable - paye_deducted
                result_type = 'additional' if additional_tax > 0 else 'balanced'
            
            # Calculate effective tax rate
            effective_rate = (total_tax_payable / total_gross_income * 100) if total_gross_income > 0 else 0
            
            # === NTA 2025 COMPREHENSIVE RESULT ===
            result = {
                'exempt': False,
                'total_gross_income': total_gross_income,
                'total_deductions': total_deductions,
                'chargeable_income': chargeable_income,
                'tax_payable': total_tax_payable,
                'paye_deducted': paye_deducted,
                'refund_amount': refund_amount,
                'additional_tax': additional_tax,
                'result_type': result_type,
                'effective_rate': round(effective_rate, 2),
                'deductions_breakdown': {
                    'pension': round(pension_deduction, 2),
                    'nhis': round(nhis_deduction, 2),
                    'nhf': round(nhf_deduction, 2),
                    'rent_relief': round(rent_relief, 2),
                    'life_insurance': life_insurance,
                    'mortgage_interest': mortgage_interest
                },
                'income_breakdown': {
                    'salary': gross_income,
                    'crypto_gains': crypto_gains,
                    'capital_gains': capital_gains,
                    'severance_pay': severance
                }
            }
            
            return result
            
        except Exception as e:
            print(f"Calculation error: {str(e)}")
            raise
    
    @staticmethod
    def calculate_vat(data):
        """Calculate VAT"""
        try:
            amount = float(data.get('amount', 0))
            calculation_type = data.get('type', 'net')
            vat_rate = 0.075  # 7.5%
            
            if calculation_type == 'net':
                vat_amount = amount * vat_rate
                gross_amount = amount + vat_amount
                return {
                    'type': 'net_to_gross',
                    'net_amount': amount,
                    'vat_amount': vat_amount,
                    'gross_amount': gross_amount,
                    'vat_rate': vat_rate * 100
                }
            elif calculation_type == 'gross':
                net_amount = amount / (1 + vat_rate)
                vat_amount = amount - net_amount
                return {
                    'type': 'gross_to_net',
                    'gross_amount': amount,
                    'vat_amount': vat_amount,
                    'net_amount': net_amount,
                    'vat_rate': vat_rate * 100
                }
                
        except Exception as e:
            raise
    
    @staticmethod
    def calculate_rent_relief(data):
        """Calculate Rent Relief"""
        try:
            rent_paid = float(data.get('rent_paid', 0))
            relief_percentage = 0.20
            max_relief = 500000
            
            calculated_relief = rent_paid * relief_percentage
            actual_relief = min(calculated_relief, max_relief)
            
            return {
                'rent_paid': rent_paid,
                'calculated_relief': calculated_relief,
                'actual_relief': actual_relief,
                'max_limit': max_relief,
                'percentage': relief_percentage * 100,
                'tax_saving': actual_relief * 0.20
            }
            
        except Exception as e:
            raise