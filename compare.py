from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Read the Dank_Assets.txt file and return the asset names
def load_dank_assets():
    try:
        with open("Dank_Assets.txt", "r") as file:
            # Read and clean up the asset names in the file
            dank_assets = {line.strip() for line in file.readlines()}
        return dank_assets
    except FileNotFoundError:
        return set()

# Fetch assets from the API based on a wallet address
def fetch_assets_from_api(address, page=1, limit=100):
    api_url = f"https://tokenscan.io/api/balances/{address}?page={page}&limit={limit}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Check if 'data' is present and contains assets
        if 'data' in data and data['data']:
            return {
                asset['asset']: asset['quantity']  # Using asset name as key for easy comparison
                for asset in data['data']
            }
        else:
            return {}

    except requests.exceptions.RequestException:
        return {}

# Retrieve all assets by iterating through paginated responses
def get_all_assets(address, dank_assets):
    all_assets = {}
    page = 1
    limit = 100

    while True:
        assets = fetch_assets_from_api(address, page, limit)
        if not assets:
            break
        # Filter assets to only include those in Dank_Assets.txt
        filtered_assets = {asset: quantity for asset, quantity in assets.items() if asset in dank_assets}
        all_assets.update(filtered_assets)
        page += 1

    return all_assets

# Compare assets between two wallet addresses
def compare_wallets(your_address, their_address):
    dank_assets = load_dank_assets()  # Load the Dank assets list once
    your_assets = get_all_assets(your_address, dank_assets)
    their_assets = get_all_assets(their_address, dank_assets)

    unique_assets = {asset: quantity for asset, quantity in their_assets.items() if asset not in your_assets}
    return {
        "your_assets_count": len(your_assets),
        "their_assets_count": len(their_assets),
        "unique_assets": unique_assets
    }

# Define the main route to render the input form and display results
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        your_address = request.form['your_address']
        their_address = request.form['their_address']
        
        # Perform the comparison and store the result
        result = compare_wallets(your_address, their_address)
        
    return render_template('index.html', result=result)

if __name__ == "__main__":
    app.run(debug=True)