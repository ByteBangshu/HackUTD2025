from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import pandas as pd
import os

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

@csrf_exempt
def predict(request):
    """
    API endpoint to predict car model based on user preferences
    Returns top 3 matches
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
        fuelType = data.get('fuelType')
        mpg = data.get('mpg')
        financeMonthly = data.get('finance_monthly')
        leaseMonthly = data.get('lease_monthly')
        horsepower = data.get('horsepower')
        
        # DEBUG: Print received data
        print("=" * 50)
        print("RECEIVED DATA:")
        print(f"Year: {year}")
        print(f"Max Price: {max_price}")
        print(f"Transmission: {transmission}")
        print(f"Max Mileage: {max_mileage}")
        print(f"Fuel Type: {fuelType}")
        print(f"MPG: {mpg}")
        print(f"Finance Monthly: {financeMonthly}")
        print(f"Lease Monthly: {leaseMonthly}")
        print(f"Horsepower: {horsepower}")
        print("=" * 50)
        
        # Load the CSV file with proper path handling
        csv_path = os.path.join(settings.BASE_DIR, 'toyota.csv')
        
        # Check if file exists
        if not os.path.exists(csv_path):
            # Try alternative path in 'data' folder
            csv_path = os.path.join(settings.BASE_DIR, 'data', 'toyota.csv')
            if not os.path.exists(csv_path):
                return JsonResponse({
                    'matches': [],
                    'message': f'Database file not found. Please contact support.'
                }, status=200)
        
        df = pd.read_csv(csv_path)
        
        # Clean column names (remove extra spaces)
        df.columns = df.columns.str.strip()
        
        # DEBUG: Print initial dataframe info
        print(f"Total records in CSV: {len(df)}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Start with all data
        filtered_df = df.copy()
        print(f"Starting with {len(filtered_df)} records")
        
        # Apply filters with STRICT matching and 5% tolerance
        if year:
            year_val = int(year)
            # STRICT: Exact year match only (0% tolerance)
            filtered_df = filtered_df[filtered_df['year'] == year_val]
            print(f"After STRICT year filter (={year_val}): {len(filtered_df)} records")
        
        if max_price:
            price_val = float(max_price)
            # Allow only 5% higher price
            filtered_df = filtered_df[filtered_df['price'] <= price_val * 1.05]
            print(f"After price filter (≤${price_val * 1.05:,.0f}): {len(filtered_df)} records")
        
        if transmission:
            # STRICT: Exact match only for transmission
            filtered_df = filtered_df[filtered_df['transmission'].str.strip().str.lower() == transmission.lower()]
            print(f"After transmission filter ({transmission}): {len(filtered_df)} records")
        
        if max_mileage:
            mileage_val = float(max_mileage)
            # Allow only 5% higher mileage
            filtered_df = filtered_df[filtered_df['mileage'] <= mileage_val * 1.05]
            print(f"After mileage filter (≤{mileage_val * 1.05:,.0f}): {len(filtered_df)} records")
        
        if fuelType:
            # STRICT: Exact match only for fuel type
            filtered_df = filtered_df[filtered_df['fuelType'].str.strip().str.lower() == fuelType.lower()]
            print(f"After fuel type filter ({fuelType}): {len(filtered_df)} records")
        
        if mpg:
            mpg_val = float(mpg)
            # Allow only 5% lower MPG
            filtered_df = filtered_df[filtered_df['mpg'] >= mpg_val * 0.95]
            print(f"After MPG filter (≥{mpg_val * 0.95:.1f}): {len(filtered_df)} records")
        
        if financeMonthly:
            finance_val = float(financeMonthly)
            # Allow only 5% higher monthly payment
            filtered_df = filtered_df[filtered_df['finance_monthly'] <= finance_val * 1.05]
            print(f"After finance filter (≤${finance_val * 1.05:.2f}/mo): {len(filtered_df)} records")
        
        if leaseMonthly:
            lease_val = float(leaseMonthly)
            # Allow only 5% higher monthly payment
            filtered_df = filtered_df[filtered_df['lease_monthly'] <= lease_val * 1.05]
            print(f"After lease filter (≤${lease_val * 1.05:.2f}/mo): {len(filtered_df)} records")
        
        if horsepower:
            hp_val = float(horsepower)
            # Allow only 5% lower horsepower
            filtered_df = filtered_df[filtered_df['horsepower'] >= hp_val * 0.95]
            print(f"After horsepower filter (≥{hp_val * 0.95:.0f}): {len(filtered_df)} records")
        
        print("=" * 50)
        
        # Find the TOP 3 matches based on similarity to user input
        if not filtered_df.empty:
            # Calculate similarity score for each car
            def calculate_similarity_score(row):
                score = 0.0
                total_weight = 0.0
                
                # Price similarity (weight: 3) - lower is better, closer to user input is better
                if max_price:
                    price_val = float(max_price)
                    price_diff = abs(row['price'] - price_val) / price_val
                    score += (1 - price_diff) * 3
                    total_weight += 3
                
                # Mileage similarity (weight: 2) - lower is better
                if max_mileage:
                    mileage_val = float(max_mileage)
                    mileage_diff = abs(row['mileage'] - mileage_val) / mileage_val
                    score += (1 - mileage_diff) * 2
                    total_weight += 2
                
                # MPG similarity (weight: 2) - closer to user input is better
                if mpg:
                    mpg_val = float(mpg)
                    mpg_diff = abs(row['mpg'] - mpg_val) / mpg_val
                    score += (1 - mpg_diff) * 2
                    total_weight += 2
                
                # Finance monthly similarity (weight: 2)
                if financeMonthly:
                    finance_val = float(financeMonthly)
                    finance_diff = abs(row['finance_monthly'] - finance_val) / finance_val
                    score += (1 - finance_diff) * 2
                    total_weight += 2
                
                # Lease monthly similarity (weight: 2)
                if leaseMonthly:
                    lease_val = float(leaseMonthly)
                    lease_diff = abs(row['lease_monthly'] - lease_val) / lease_val
                    score += (1 - lease_diff) * 2
                    total_weight += 2
                
                # Horsepower similarity (weight: 1.5) - closer to user input is better
                if horsepower:
                    hp_val = float(horsepower)
                    hp_diff = abs(row['horsepower'] - hp_val) / hp_val
                    score += (1 - hp_diff) * 1.5
                    total_weight += 1.5
                
                # Normalize score (0-100)
                if total_weight > 0:
                    return (score / total_weight) * 100
                return 0
            
            # Calculate similarity scores for all filtered cars
            filtered_df['similarity_score'] = filtered_df.apply(calculate_similarity_score, axis=1)
            
            # Sort by similarity score (highest first), then by price (lowest first) as tiebreaker
            sorted_df = filtered_df.sort_values(by=['similarity_score', 'price'], ascending=[False, True])
            
            # Get top 3 matches
            top_matches = sorted_df.head(3)
            
            print(f"TOP 3 MATCHES FOUND:")
            matches_list = []
            
            for idx, (_, match) in enumerate(top_matches.iterrows(), 1):
                print(f"\nMatch #{idx} (Similarity: {match['similarity_score']:.2f}%): {match['model']}")
                print(f"  Year: {match['year']}")
                print(f"  Price: ${match['price']:,.0f}")
                print(f"  Transmission: {match['transmission']}")
                print(f"  Mileage: {match['mileage']:,.0f}")
                print(f"  Fuel Type: {match['fuelType']}")
                print(f"  MPG: {match['mpg']:.1f}")
                print(f"  Finance: ${match['finance_monthly']:.2f}/mo")
                print(f"  Lease: ${match['lease_monthly']:.2f}/mo")
                print(f"  Horsepower: {match['horsepower']}")
                
                # Format match data
                match_data = {
                    'model': str(match['model']),
                    'year': str(int(match['year'])),
                    'price': f"${int(match['price']):,}",
                    'mpg': f"{float(match['mpg']):.1f} MPG",
                    'horsepower': f"{int(match['horsepower'])} HP",
                    'transmission': str(match['transmission']).strip(),
                    'mileage': f"{int(match['mileage']):,} miles",
                    'fuelType': str(match['fuelType']).strip(),
                    'finance_monthly': f"${float(match['finance_monthly']):.2f}/mo",
                    'lease_monthly': f"${float(match['lease_monthly']):.2f}/mo",
                    'similarity_score': f"{match['similarity_score']:.1f}%"
                }
                matches_list.append(match_data)
            
            print("=" * 50)
            
            response_data = {
                'matches': matches_list,
                'total_matches': int(len(filtered_df))
            }
            
            return JsonResponse(response_data)
        else:
            print("NO MATCHES FOUND")
            print("=" * 50)
            # No matches found
            return JsonResponse({
                'matches': [],
                'message': 'No matching cars found based on your criteria. Try adjusting your filters.'
            }, status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'matches': [],
            'message': 'Invalid request format'
        }, status=200)
    except FileNotFoundError:
        return JsonResponse({
            'matches': [],
            'message': 'Database file not found. Please contact support.'
        }, status=200)
    except KeyError as e:
        return JsonResponse({
            'matches': [],
            'message': f'Missing data column: {str(e)}'
        }, status=200)
    except Exception as e:
        import traceback
        print("ERROR:", str(e))
        print(traceback.format_exc())
        return JsonResponse({
            'matches': [],
            'message': f'An error occurred: {str(e)}'
        }, status=200)
