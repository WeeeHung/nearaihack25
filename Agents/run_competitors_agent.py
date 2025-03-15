import os
import json
from competitors_agent import CompetitorsAgent
import dotenv

# Load environment variables from .env file if available
dotenv.load_dotenv()

def pretty_print_json(data):
    """Print JSON data in a readable format"""
    print(json.dumps(data, indent=2))

def run_test_with_minut():
    """Run the competitors agent with Minut data"""
    # Create a CompetitorsAgent instance
    agent = CompetitorsAgent()
    
    # Define Minut company information based on the TechCrunch article
    company_info = """
    Company Name: Minut
    
    Description: Minut has built a privacy-forward hardware solution that helps Airbnb hosts "keep an eye" on their 
    properties without trampling over guests' privacy. The company's slogan is "We're the co-host that cares for your 
    home, guests and community."
    
    Business: Hardware IoT device with subscription service for short-term rental hosts.
    
    Funding: Raised a $15M Series B round led by Almaz Capital in December 2021.
    
    Traction: Has 30,000 users in more than 100 countries. Subscription model that scales with growing ARR.
    
    Key Product Features: Sensor for every short-term rental that respects guest privacy while monitoring properties.
    """
    
    # Create a mock shared dictionary
    shared = {"company_info": company_info}
    
    print("="*80)
    print("RUNNING COMPETITORS AGENT WITH MINUT DATA")
    print("="*80)
    print("\nCOMPANY INFO:")
    print(company_info)
    
    # Run prep method
    print("\n" + "="*80)
    print("RUNNING PREP METHOD")
    print("="*80)
    prep_result = agent.prep(shared)
    print("Prep Result:", prep_result)
    
    # Run exec method
    print("\n" + "="*80)
    print("RUNNING EXEC METHOD (this might take a while as it makes real API calls)")
    print("="*80)
    exec_result = agent.exec(prep_result)
    
    # Print exec results
    print("\n" + "="*80)
    print("EXEC RESULTS")
    print("="*80)
    
    # Count competitors
    direct_count = len(exec_result.get("direct_competitors", []))
    indirect_count = len(exec_result.get("indirect_competitors", []))
    print(f"Found {direct_count} direct competitors and {indirect_count} indirect competitors.\n")
    
    # Print direct competitors
    print("DIRECT COMPETITORS:")
    for i, competitor in enumerate(exec_result.get("direct_competitors", []), 1):
        print(f"\n--- Direct Competitor #{i} ---")
        if "companyProfile" in competitor:
            profile = competitor["companyProfile"]
            print(f"Name: {profile.get('name', 'N/A')}")
            print(f"Year Founded: {profile.get('yearFounded', 'N/A')}")
            print(f"Headquarters: {profile.get('headquarters', 'N/A')}")
            print(f"Website: {profile.get('website', 'N/A')}")
            print(f"Funding Stage: {profile.get('fundingStage', 'N/A')}")
            print(f"Total Funds Raised: {profile.get('totalFundsRaised', 'N/A')}")
        
        if "description" in competitor:
            print(f"\nDescription: {competitor['description']}")
        
        if "comparisons" in competitor:
            print("\nSimilarities:")
            for similarity in competitor["comparisons"].get("similarities", []):
                print(f"- {similarity}")
                
            print("\nDifferences:")
            for difference in competitor["comparisons"].get("differences", []):
                print(f"- {difference}")
    
    # Print indirect competitors (first 3 only to save space)
    print("\n\nINDIRECT COMPETITORS (showing first 3):")
    for i, competitor in enumerate(exec_result.get("indirect_competitors", [])[:3], 1):
        print(f"\n--- Indirect Competitor #{i} ---")
        if "companyProfile" in competitor:
            profile = competitor["companyProfile"]
            print(f"Name: {profile.get('name', 'N/A')}")
            print(f"Year Founded: {profile.get('yearFounded', 'N/A')}")
            print(f"Headquarters: {profile.get('headquarters', 'N/A')}")
            print(f"Website: {profile.get('website', 'N/A')}")
            print(f"Funding Stage: {profile.get('fundingStage', 'N/A')}")
            print(f"Total Funds Raised: {profile.get('totalFundsRaised', 'N/A')}")
        
        if "description" in competitor:
            print(f"\nDescription: {competitor['description']}")
    
    # Run post method
    print("\n" + "="*80)
    print("RUNNING POST METHOD")
    print("="*80)
    post_result = agent.post(shared, prep_result, exec_result)
    print("Post Result:", post_result)
    print("Competitors data has been stored in shared dictionary")
    
    # Save results to file
    output_file = "minut_competitors_results.json"
    with open(output_file, "w") as f:
        json.dump(exec_result, f, indent=2)
    
    print(f"\nFull results saved to {output_file}")

if __name__ == "__main__":
    run_test_with_minut()