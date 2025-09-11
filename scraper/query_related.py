# Common ocean-related hazards
hazards = [
    "tsunami",
    "storm surge",
    "cyclone",
    "high tide",
    "high waves",
    "coastal flooding",
    "coastal erosion",
    "rough sea"
]

# Key coastal locations 
locations = [
    # East Coast
    "Kolkata", "Digha", "Puri", "Paradip", "Visakhapatnam", "Kakinada",
    "Chennai", "Thoothukudi", "Nagapattinam", "Puducherry",
    
    # West Coast
    "Kandla", "Dwarka", "Mumbai", "Ratnagiri", "Panaji", "Mangaluru",
    "Kochi", "Alappuzha", "Thiruvananthapuram",
    
    # Islands
    "Port Blair", "Agatti", "Kavaratti"
]

def generate_queries():
    queries = [{'query':f"{hazard} {location}", 'location':location, 'hazard':hazard} for hazard in hazards for location in locations]
    return queries