import pandas as pd

# Load the data
df = pd.read_csv("toyota.csv")

# Clean column names (remove extra spaces)
df.columns = df.columns.str.strip()

print("=== Toyota Car Finder ===\n")
print(f"Total records: {len(df)}\n")

print("Enter your preferences (leave blank to skip any filter):\n")

# Get user inputs
year = input("Enter year : ").strip()
max_price = input("Enter max price : ").strip()
transmission = input("Enter transmission type (Manual/Automatic): ").strip()
max_mileage = input("Enter max mileage : ").strip()
fuelType = input("Enter fuel type (Gasoline/Diesel/Hybrid): ").strip()
mpg = input("Enter mph: ").strip()
financeMonthly = input("Money monthly: ")
LeaseMonthly = input("Lease monthly: ")
housePower = input("horsePower: ")
# Start with all data
filtered_df = df.copy()

# Apply filters one by one (safer than using query string)
if year:
    filtered_df = filtered_df[filtered_df['year'] == int(year)]
    
if max_price:
    filtered_df = filtered_df[filtered_df['price'] <= float(max_price)]
    
if transmission:
    filtered_df = filtered_df[filtered_df['transmission'].str.strip() == transmission]
    
if max_mileage:
    filtered_df = filtered_df[filtered_df['mileage'] <= float(max_mileage)]
    
if fuelType:
    filtered_df = filtered_df[filtered_df['fuelType'].str.strip() == fuelType]

if mpg:
    filtered_df = filtered_df[filtered_df['mpg'] <= float(mpg)]

if financeMonthly:
    filtered_df = filtered_df[filtered_df['finance_monthly'] <= float(financeMonthly)]

if LeaseMonthly:
    filtered_df = filtered_df[filtered_df['lease_monthly'] <= float(LeaseMonthly)]

if housePower:
    filtered_df = filtered_df[filtered_df['horsepower'] <= float(housePower)]
    
# Find and display the best match (lowest price)
if not filtered_df.empty:
    best_match = filtered_df.sort_values(by='price').head(1)
    print("\n" + "="*50)
    print("BEST MATCHING MODEL:")
    print("="*50)
    print(best_match.to_string(index=False))
    print("\n" + "="*50)
    print(f"Total matches found: {len(filtered_df)}")
else:
    print("\n" + "="*50)
    print("No matching models found based on your criteria.")
    print("Try adjusting your filters.")
    print("="*50)