from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from collections import defaultdict
import pandas as pd

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

@csrf_exempt
def predict(request):
    """
    API endpoint to predict car model based on user preferences
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    
    try:
        data = json.loads(request.body.decode())
        
        # Extract form data
        year = data.get('year')
        price = data.get('price')
        transmission = data.get('transmission')
        mileage = data.get('mileage')
        fuel_type = data.get('fuelType')
        mpg = data.get('mpg')
        finance_monthly = data.get('finance_monthly')
        lease_monthly = data.get('lease_monthly')
        horsepower = data.get('horsepower')
        
        # TODO: Implement actual ML model prediction logic here
        # For now, returning a mock response
        df: pd.DataFrame = pd.read_csv('toyota.csv')
        temp_mixed_list = []
        recommended_models = dict()
        for index, row in df.iterrows():
          temp_mixed_list.append(str(row['year']))
          temp_mixed_list.append(str(row['price']))
          temp_mixed_list.append(str(row['transmission']))
          temp_mixed_list.append(str(row['mileage']))
          temp_mixed_list.append(str(row['fuelType']))
          temp_mixed_list.append(str(row['mpg']))
          temp_mixed_list.append(str(row['finance_monthly']))
          temp_mixed_list.append(str(row['lease_monthly']))
          temp_mixed_list.append(str(row['horsepower']))
          recommended_models[tuple(temp_mixed_list)] = str(row['model'])
          temp_mixed_list.clear()
        
        # # Mock response based on criteria
        # recommended_models = {
        #     'Gasoline': 'Toyota Camry SE',
        #     'Hybrid': 'Toyota Prius Prime',
        #     'Diesel': 'Toyota Hilux',
        #     'Electric': 'Toyota bZ4X'
        # }
        user_input = (str(year), str(price), str(transmission), str(mileage), str(fuel_type), str(mpg), str(finance_monthly), str(lease_monthly), str(horsepower))
        model = recommended_models.get(user_input, 'Toyota Camry')
        
        response_data = {
            'model': model,
            'year': year,
            'price': f"${int(price):,}",
            'mpg': f"{mpg} MPG",
            'horsepower': f"{horsepower} HP",
            'transmission': transmission,
            'finance_monthly': f"${finance_monthly}/mo",
            'lease_monthly': f"${lease_monthly}/mo"
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
