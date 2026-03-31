"""
Google Trends Data Fetcher
Fetches data from Google Trends every 5 minutes using pytrends
"""

import time
import pandas as pd
from datetime import datetime
from pytrends.request import TrendReq
import os
import json

# Configuration
KEYWORDS = ["python", "artificial intelligence"]  # Add your keywords here (max 5)
TIMEFRAME = "now 7-d"  # Options: 'now 1-H', 'now 4-H', 'now 1-d', 'now 7-d', 'today 1-m', 'today 3-m', 'today 12-m'
GEO = ""  # Leave empty for worldwide, or use country code like 'US', 'PK', 'GB'
FETCH_INTERVAL = 300  # 5 minutes in seconds
OUTPUT_FOLDER = "trends_data"


def create_output_folder():
    """Create output folder if it doesn't exist"""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created output folder: {OUTPUT_FOLDER}")


def fetch_trends_data(pytrends, keywords):
    """Fetch trends data for given keywords"""
    try:
        # Build payload
        pytrends.build_payload(keywords, cat=0, timeframe=TIMEFRAME, geo=GEO, gprop="")
        
        # Get interest over time
        interest_over_time = pytrends.interest_over_time()
        
        # Get related queries
        related_queries = pytrends.related_queries()
        
        # Get interest by region
        interest_by_region = pytrends.interest_by_region(resolution="COUNTRY", inc_low_vol=True)
        
        return {
            "interest_over_time": interest_over_time,
            "related_queries": related_queries,
            "interest_by_region": interest_by_region
        }
    except Exception as e:
        print(f"Error fetching trends data: {e}")
        return None


def save_data(data, timestamp):
    """Save fetched data to CSV and JSON files"""
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    
    # Save interest over time
    if data["interest_over_time"] is not None and not data["interest_over_time"].empty:
        filename = f"{OUTPUT_FOLDER}/interest_over_time_{timestamp_str}.csv"
        data["interest_over_time"].to_csv(filename)
        print(f"  Saved: {filename}")
    
    # Save interest by region
    if data["interest_by_region"] is not None and not data["interest_by_region"].empty:
        filename = f"{OUTPUT_FOLDER}/interest_by_region_{timestamp_str}.csv"
        data["interest_by_region"].to_csv(filename)
        print(f"  Saved: {filename}")
    
    # Save related queries as JSON
    if data["related_queries"]:
        filename = f"{OUTPUT_FOLDER}/related_queries_{timestamp_str}.json"
        # Convert DataFrames in related_queries to dictionaries
        related_queries_dict = {}
        for keyword, queries in data["related_queries"].items():
            related_queries_dict[keyword] = {}
            for query_type, df in queries.items():
                if df is not None and not df.empty:
                    related_queries_dict[keyword][query_type] = df.to_dict(orient="records")
                else:
                    related_queries_dict[keyword][query_type] = []
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(related_queries_dict, f, indent=2, ensure_ascii=False)
        print(f"  Saved: {filename}")


def fetch_and_save():
    """Main function to fetch and save trends data"""
    timestamp = datetime.now()
    print(f"\n{'='*50}")
    print(f"Fetching Google Trends data at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Keywords: {KEYWORDS}")
    print(f"{'='*50}")
    
    # Initialize pytrends
    pytrends = TrendReq(hl="en-US", tz=360)
    
    # Fetch data
    data = fetch_trends_data(pytrends, KEYWORDS)
    
    if data:
        save_data(data, timestamp)
        print("Data fetched and saved successfully!")
    else:
        print("Failed to fetch data.")
    
    return data


def get_realtime_trending():
    """Get real-time trending searches"""
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        trending = pytrends.trending_searches(pn="united_states")  # Change country as needed
        return trending
    except Exception as e:
        print(f"Error fetching trending searches: {e}")
        return None


def main():
    """Main loop - fetches data every 5 minutes"""
    print("="*60)
    print("Google Trends Data Fetcher")
    print("="*60)
    print(f"Keywords: {KEYWORDS}")
    print(f"Timeframe: {TIMEFRAME}")
    print(f"Region: {GEO if GEO else 'Worldwide'}")
    print(f"Fetch interval: {FETCH_INTERVAL} seconds ({FETCH_INTERVAL//60} minutes)")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print("="*60)
    print("\nPress Ctrl+C to stop the script\n")
    
    # Create output folder
    create_output_folder()
    
    fetch_count = 0
    
    try:
        while True:
            fetch_count += 1
            print(f"\n[Fetch #{fetch_count}]")
            
            # Fetch and save data
            fetch_and_save()
            
            # Also get real-time trending (optional)
            print("\nTop Trending Searches (US):")
            trending = get_realtime_trending()
            if trending is not None:
                print(trending.head(10).to_string(index=False))
            
            # Wait for next fetch
            print(f"\nNext fetch in {FETCH_INTERVAL//60} minutes...")
            print(f"Waiting until: {(datetime.now() + pd.Timedelta(seconds=FETCH_INTERVAL)).strftime('%H:%M:%S')}")
            
            time.sleep(FETCH_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nScript stopped by user.")
        print(f"Total fetches completed: {fetch_count}")


if __name__ == "__main__":
    main()

