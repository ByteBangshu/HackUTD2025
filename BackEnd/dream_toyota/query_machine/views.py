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
    API endpoint to find all matching car models based on user preferences using CSV data.
    Returns all matches sorted by price (lowest first).
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    
    try:
        data = json.loads(request.body.decode())
        
        # Extract form data from user input
        year = data.get('year', '').strip()
        max_price = data.get('price', '').strip()
        transmission = data.get('transmission', '').strip()
        max_mileage = data.get('mileage', '').strip()
        fuel_type = data.get('fuelType', '').strip()
        min_mpg = data.get('mpg', '').strip()
        max_finance_monthly = data.get('finance_monthly', '').strip()
        max_lease_monthly = data.get('lease_monthly', '').strip()
        min_horsepower = data.get('horsepower', '').strip()
        
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
        
        # Apply filters one by one (same logic as test.py)
        
        # Year - exact match
        if year:
            filtered_df = filtered_df[filtered_df['year'] == int(year)]
        
        # Price - maximum threshold
        if max_price:
            filtered_df = filtered_df[filtered_df['price'] <= float(max_price)]
        
        # Transmission - exact match
        if transmission:
            filtered_df = filtered_df[filtered_df['transmission'].str.strip() == transmission]
        
        # Mileage - maximum threshold
        if max_mileage:
            filtered_df = filtered_df[filtered_df['mileage'] <= float(max_mileage)]
        
        # Fuel Type - exact match
        if fuel_type:
            filtered_df = filtered_df[filtered_df['fuelType'].str.strip() == fuel_type]
        
        # MPG - minimum threshold
        if min_mpg:
            filtered_df = filtered_df[filtered_df['mpg'] >= float(min_mpg)]
        
        # Finance Monthly - maximum threshold
        if max_finance_monthly:
            filtered_df = filtered_df[filtered_df['finance_monthly'] <= float(max_finance_monthly)]
        
        # Lease Monthly - maximum threshold
        if max_lease_monthly:
            filtered_df = filtered_df[filtered_df['lease_monthly'] <= float(max_lease_monthly)]
        
        # Horsepower - minimum threshold
        if min_horsepower:
            filtered_df = filtered_df[filtered_df['horsepower'] >= float(min_horsepower)]
        
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
                'message': 'No matching models found based on your criteria. Try adjusting your filters.',
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
    except ValueError as e:
        return JsonResponse({
            "error": f"Invalid input value: {str(e)}",
            "message": "Please ensure all numeric fields contain valid numbers"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "message": "An error occurred while processing your request"
        }, status=500)