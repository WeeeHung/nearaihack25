import openai
import json
from base_agent import BaseAgent

class CompetitorsAgent(BaseAgent):
    def __init__(self, name="CompetitorsAgent"):
        """
        Initialize the competitors agent with specific functionality.
        
        Args:
            name (str): Name of the agent
        """
        super().__init__(name)
        
        # Load API keys from environment variables
        self._load_api_keys()
        
        # Initialize OpenAI client
        self.client = openai.Client(api_key=self.api_keys.get("OPENAI_API_KEY"))
    
    def prep(self, shared):
        """
        Prepare data for execution. Extract the company information from shared store.
        
        Args:
            shared (dict): Shared data store
            
        Returns:
            str: Company information to search for competitors
        """
        return shared.get("company_info", "")
    
    def exec(self, company_info):
        """
        Execute a search for competitors using the OpenAI API.
        
        Args:
            company_info (str): Information about the company to find competitors for
            
        Returns:
            dict: Structured data about competitors
        """
        try:
            # First, search for direct and indirect competitors
            search_prompt = f"""
                I need to find comprehensive information about competitors for the following company:
                {company_info}

                Please identify AT LEAST 10 competitors, clearly categorizing them as:
                1. Direct competitors (same technology, same business vertical)
                2. Indirect competitors (similar technology but different vertical, or other combinations)

                For each competitor, include:
                - Company name
                - Year founded
                - Headquarters location
                - Company website
                - Funding stage
                - Last funded amount
                - Total funds raised
                - Last valuation (if available)
                - Key investors

                Please conduct a thorough search using real-time information and ensure the results are accurate and up-to-date.
                """
            
            # Execute search using OpenAI's web search capabilities
            response = self.client.chat.completions.create(
                model="gpt-4o-search-preview",
                web_search_options={},
                messages=[
                    {
                        "role": "user", 
                        "content": search_prompt
                    }
                ],
            )
            
            # Extract initial competitor data
            competitors_data = response.choices[0].message.content if response.choices else "No response"
            
            # Now collect detailed comparison information for each competitor
            structured_competitors = self._structure_competitors_data(competitors_data, company_info)

            print("STRUCTURED COMPETITORS: ", structured_competitors)
            
            return structured_competitors
            
        except Exception as e:
            print(f"Error executing search: {e}")
            raise e
    
    def _structure_competitors_data(self, competitors_data, company_info):
        """
        Structure competitor data and get detailed comparisons
        
        Args:
            competitors_data (str): Initial search results with competitor information
            company_info (str): Original company information
            
        Returns:
            dict: Fully structured competitor data
        """
        # Extract competitor names from initial search results
        extraction_prompt = f"""
            Given the following search results about competitors:

            {competitors_data}

            Extract the names of ALL competitors mentioned (both direct and indirect).
            Format the response as a JSON array of strings containing ONLY the company names.
        """
        
        try:
            # Use the o3mini model from the base agent
            o3mini_model = self.get_o3mini_model(temperature=0.7)
            
            # Create messages for the API call
            messages = [{"role": "user", "content": extraction_prompt}]
            
            # Use the client directly but with the model from get_o3mini_model
            response = self.client.chat.completions.create(
                model=o3mini_model,  # Using the model string from base_agent
                messages=messages,
                response_format={"type": "json_object"},
            )
            
            competitors_json = json.loads(response.choices[0].message.content)
            competitor_names = competitors_json.get("competitors", [])
            
            # If the response doesn't contain a "competitors" key, try to extract from the raw content
            if not competitor_names and isinstance(competitors_json, list):
                competitor_names = competitors_json
            elif not competitor_names:
                # Try to find any list in the JSON
                for key, value in competitors_json.items():
                    if isinstance(value, list) and len(value) > 0:
                        competitor_names = value
                        break
            
            # Fallback if we still don't have competitor names
            if not competitor_names:
                # Try to extract the names through another prompt
                extraction_prompt = f"""
                    Extract ONLY the company names (both direct and indirect competitors) from this text:

                    {competitors_data}

                    Return ONLY a JSON array of strings with the company names. Do not include any other information.
                """
                response = self.client.chat.completions.create(
                    model="o3-mini",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    response_format={"type": "json_object"},
                )
                raw_json = json.loads(response.choices[0].message.content)
                # Get the first list found in the JSON
                for key, value in raw_json.items():
                    if isinstance(value, list):
                        competitor_names = value
                        break
            
            # Final fallback
            if not competitor_names:
                # Parse manually for company names with another approach
                lines = competitors_data.split('\n')
                competitor_names = []
                for line in lines:
                    if ":" in line and any(word in line.lower() for word in ["company", "competitor", "name"]):
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            competitor_names.append(parts[1].strip())
            
            # Get detailed information for each competitor
            result = {
                "direct_competitors": [],
                "indirect_competitors": []
            }
            
            # Determine if each competitor is direct or indirect and get detailed info
            for name in competitor_names:
                competitor_info = self._get_competitor_details(name, company_info)
                if competitor_info:
                    category = "direct_competitors" if competitor_info["is_direct"] else "indirect_competitors"
                    result[category].append(competitor_info)
            
            return result
            
        except Exception as e:
            print(f"Error structuring competitor data: {e}")
            return {
                "direct_competitors": [],
                "indirect_competitors": [],
                "error": str(e),
                "raw_data": competitors_data
            }
    
    def _get_competitor_details(self, competitor_name, original_company_info):
        """
        Get detailed information about a competitor and comparison to original company
        
        Args:
            competitor_name (str): Name of the competitor
            original_company_info (str): Information about the original company
            
        Returns:
            dict: Structured competitor information
        """
        try:
            details_prompt = f"""
                Search for detailed information about {competitor_name} and provide a comparison with the following company:

                Original company: {original_company_info}

                Return a JSON object with the following structure:
                {{
                "companyProfile": {{
                    "name": "{competitor_name}",
                    "yearFounded": "",
                    "headquarters": "",
                    "website": "",
                    "fundingStage": "",
                    "lastFundedAmount": "",
                    "totalFundsRaised": "",
                    "lastValuation": "",
                    "investors": []
                }},
                "description": "Description of what the company does in comparison to the original company",
                "comparisons": {{
                    "similarities": ["similarity1", "similarity2", "..."],
                    "differences": ["difference1", "difference2", "..."]
                }},
                "is_direct": true/false
                }}

                The comparisons section is EXTREMELY important. Make sure to include at least 3 specific similarities 
                and 3 specific differences between {competitor_name} and the original company.
                Make sure to fill in all fields with accurate data. The "is_direct" field should be true if this is a 
                direct competitor (same technology and same business vertical) and false if it's an indirect competitor.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-search-preview",
                web_search_options={},
                messages=[{"role": "user", "content": details_prompt}],
                max_tokens=5000,
            )
            
            response_content = response.choices[0].message.content
            
            # Clean up and extract JSON
            json_str = ""
            if "```json" in response_content:
                json_str = response_content.split("```json")[1].split("```")[0].strip()
            elif "```" in response_content:
                json_str = response_content.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_content.strip()
            
            # Parse the JSON
            competitor_details = json.loads(json_str)
            
            # Validate and fix the structure if needed
            if "companyProfile" not in competitor_details and "companyprofile" in competitor_details:
                # Fix capitalization
                competitor_details["companyProfile"] = competitor_details.pop("companyprofile")
                
            if "comparisons" not in competitor_details:
                # Check for other possible keys
                for key in competitor_details.keys():
                    if key.lower() == "comparisons" or key.lower() == "comparison":
                        competitor_details["comparisons"] = competitor_details.pop(key)
                        break
                else:
                    # If still not found, create an empty structure
                    competitor_details["comparisons"] = {
                        "similarities": ["No similarities found"],
                        "differences": ["No differences found"]
                    }
                    
            # Ensure sub-keys exist
            if "similarities" not in competitor_details["comparisons"]:
                competitor_details["comparisons"]["similarities"] = ["No similarities found"]
                
            if "differences" not in competitor_details["comparisons"]:
                competitor_details["comparisons"]["differences"] = ["No differences found"]
            
            # Add a debugging message
            print(f"Found {len(competitor_details['comparisons']['similarities'])} similarities and "
                  f"{len(competitor_details['comparisons']['differences'])} differences for {competitor_name}")
            
            return competitor_details
            
        except Exception as e:
            print(f"Error getting details for {competitor_name}: {e}")
            print(f"Raw response: {response.choices[0].message.content if 'response' in locals() else 'No response'}")
            
            # Return a partial result instead of None
            return {
                "name": competitor_name,
                "companyProfile": {
                    "name": competitor_name,
                    "yearFounded": "Unknown",
                    "headquarters": "Unknown",
                    "website": "Unknown",
                    "fundingStage": "Unknown",
                    "lastFundedAmount": "Unknown",
                    "totalFundsRaised": "Unknown",
                    "lastValuation": "Unknown",
                    "investors": []
                },
                "description": "Failed to retrieve full data",
                "comparisons": {
                    "similarities": ["Data retrieval error"],
                    "differences": ["Data retrieval error"]
                },
                "is_direct": False  # Default to indirect if we can't determine
            }
    
    def post(self, shared, prep_res, exec_res):
        """
        Process and store the competitor information.
        
        Args:
            shared (dict): Shared data store
            prep_res (str): Input company information
            exec_res (dict): Structured competitor data
            
        Returns:
            str: Action string for flow control
        """
        # Store the results in the shared store
        shared["competitors"] = exec_res
        
        # Count total competitors found
        total_direct = len(exec_res.get("direct_competitors", []))
        total_indirect = len(exec_res.get("indirect_competitors", []))
        
        print(f"Found {total_direct} direct competitors and {total_indirect} indirect competitors.")
        
        if total_direct + total_indirect < 10:
            print("Warning: Less than 10 competitors found. Results may not be comprehensive.")
        
        return "default"