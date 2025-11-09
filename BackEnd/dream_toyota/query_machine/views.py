from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pandas as pd
import os
from django.conf import settings

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

@csrf_exempt
def predict(request):
    """
    API endpoint to find all matching car models based on user preferences using CSV data
    Returns all matches sorted by price (lowest first)
    
    Numeric parameters allow ±10% tolerance:
    - price (max)
    - mileage (max)
    - mpg (min)
    - finance_monthly (max)
    - lease_monthly (max)
    - horsepower (min)
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    
    try:
        data = json.loads(request.body.decode())
        
        # Extract form data
        year = data.get('year')
        max_price = data.get('price')
        transmission = data.get('transmission')
        max_mileage = data.get('mileage')
        fuel_type = data.get('fuelType')
        min_mpg = data.get('mpg')
        max_finance_monthly = data.get('finance_monthly')
        max_lease_monthly = data.get('lease_monthly')
        min_horsepower = data.get('horsepower')
        
        # Load the CSV file
        csv_path = os.path.join(settings.BASE_DIR, 'toyota.csv')
        
        if not os.path.exists(csv_path):
            return JsonResponse({
                "error": "toyota.csv not found",
                "message": "Please place toyota.csv in the project root directory"
            }, status=404)
        
        df = pd.read_csv(csv_path)
        
        # Clean column names (remove extra spaces)
        df.columns = df.columns.str.strip()
        
        # Start with all data
        filtered_df = df.copy()
        
        # Apply filters one by one with ±10% tolerance for numeric fields
        
        # Year - exact match (no tolerance)
        if year:
            filtered_df = filtered_df[filtered_df['year'] == int(year)]
        
        # Price - max with +10% tolerance (user can go 10% over budget)
        if max_price:
            price_threshold = float(max_price) * 1.10  # Allow 10% over
            filtered_df = filtered_df[filtered_df['price'] <= price_threshold]
        
        # Transmission - exact match (no tolerance)
        if transmission:
            filtered_df = filtered_df[filtered_df['transmission'].str.strip() == transmission]
        
        # Mileage - max with +10% tolerance
        if max_mileage:
            mileage_threshold = float(max_mileage) * 1.10  # Allow 10% over
            filtered_df = filtered_df[filtered_df['mileage'] <= mileage_threshold]
        
        # Fuel Type - exact match (no tolerance)
        if fuel_type:
            filtered_df = filtered_df[filtered_df['fuelType'].str.strip() == fuel_type]
        
        # MPG - minimum with -10% tolerance (user accepts 10% less efficient)
        if min_mpg:
            mpg_threshold = float(min_mpg) * 0.90  # Allow 10% less
            filtered_df = filtered_df[filtered_df['mpg'] >= mpg_threshold]
        
        # Finance Monthly - max with +10% tolerance
        if max_finance_monthly:
            finance_threshold = float(max_finance_monthly) * 1.10  # Allow 10% over
            filtered_df = filtered_df[filtered_df['finance_monthly'] <= finance_threshold]
        
        # Lease Monthly - max with +10% tolerance
        if max_lease_monthly:
            lease_threshold = float(max_lease_monthly) * 1.10  # Allow 10% over
            filtered_df = filtered_df[filtered_df['lease_monthly'] <= lease_threshold]
        
        # Horsepower - minimum with -10% tolerance (user accepts 10% less power)
        if min_horsepower:
            horsepower_threshold = float(min_horsepower) * 0.90  # Allow 10% less
            filtered_df = filtered_df[filtered_df['horsepower'] >= horsepower_threshold]
        
        # Find and return all matches (sorted by price)
        if not filtered_df.empty:
            # Sort by price (lowest first)
            all_matches = filtered_df.sort_values(by='price')
            
            # Convert all matches to a list of dictionaries
            matches_list = []
            for idx, row in all_matches.iterrows():
                match_dict = {
                    'model': row['model'],
                    'year': int(row['year']),
                    'price': float(row['price']),
                    'price_formatted': f"${row['price']:,.2f}",
                    'transmission': row['transmission'],
                    'mileage': int(row['mileage']),
                    'mileage_formatted': f"{row['mileage']:,.0f} miles",
                    'fuelType': row['fuelType'],
                    'mpg': float(row['mpg']),
                    'finance_monthly': float(row['finance_monthly']),
                    'finance_monthly_formatted': f"${row['finance_monthly']:.2f}",
                    'lease_monthly': float(row['lease_monthly']),
                    'lease_monthly_formatted': f"${row['lease_monthly']:.2f}",
                    'horsepower': int(row['horsepower']),
                }
                matches_list.append(match_dict)
            
            # Prepare response with best match and all matches
            best_match = matches_list[0]
            
            response_data = {
                'success': True,
                'total_matches': len(matches_list),
                'best_match': best_match,
                'all_matches': matches_list,
                'best_price': f"${all_matches.iloc[0]['price']:,.2f}",
                'tolerance_applied': '±10% tolerance applied to numeric parameters',
                # For backward compatibility with existing frontend
                'model': best_match['model'],
                'year': str(best_match['year']),
                'price': best_match['price_formatted'],
                'mpg': f"{best_match['mpg']} MPG",
                'horsepower': f"{best_match['horsepower']} HP",
                'transmission': best_match['transmission'],
                'fuelType': best_match['fuelType'],
                'mileage': best_match['mileage_formatted'],
                'finance_monthly': best_match['finance_monthly_formatted'],
                'lease_monthly': best_match['lease_monthly_formatted'],
            }
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({
                'success': False,
                'model': 'No match found',
                'message': 'No matching models found based on your criteria (even with ±10% tolerance). Try adjusting your filters.',
                'total_matches': 0,
                'all_matches': []
            })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except FileNotFoundError:
        return JsonResponse({
            "error": "CSV file not found",
            "message": "Please ensure toyota.csv is in the project root directory"
        }, status=404)
    except KeyError as e:
        return JsonResponse({
            "error": f"Missing column in CSV: {str(e)}",
            "message": "Please check your CSV file has all required columns"
        }, status=500)
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "message": "An error occurred while processing your request"
        }, status=500)
