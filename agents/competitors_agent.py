import openai
import json
from .base_agent import BaseAgent
from nearai.agents.environment import Environment

class CompetitorsAgent(BaseAgent):
    def __init__(self, env:Environment, name="CompetitorsAgent"):
        """
        Initialize the competitors agent with specific functionality.
        
        Args:
            name (str): Name of the agent
        """
        super().__init__(env, name=name)
        self.client = openai.OpenAI(api_key=self.api_keys["OPENAI_API_KEY"])
        self.env.add_system_log("CompetitorsAgent initialized")
        self.max_retries = 3  # Maximum number of retries for JSON parsing

    def prep(self, shared):
        """
        Prepare data for execution. Extract the company information from shared store.
        
        Args:
            shared (dict): Shared data store
            
        Returns:
            str: Company information to search for competitors
        """
        return shared.get("company_info", "")
    
    def run(self, company_info):
        """
        Execute a search for competitors using the OpenAI API.
        
        Args:
            company_info (str): Information about the company to find competitors for
        
        Returns:
            dict: Structured data about competitors
        """
        self.env.add_system_log("Running CompetitorsAgent")
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
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-search-preview",
            web_search_options={},
        messages=[{"role": "user", "content": search_prompt}],
        )
        
        competitors_data = response.choices[0].message.content
        return self._structure_competitors_data(competitors_data, company_info)
    
    def _structure_competitors_data(self, competitors_data, company_info):
        """
        Structure competitor data and get detailed comparisons
        
        Args:
            competitors_data (str): Initial search results with competitor information
            company_info (str): Original company information
            
        Returns:
            dict: Fully structured competitor data
        """
        extraction_prompt = f"""
            Given the following search results about competitors:
            {competitors_data}
            Extract the names of ALL competitors mentioned (both direct and indirect).
            Format the response as a JSON object with a single key "competitors" containing an array of strings with ONLY the company names.
            Your response must be valid JSON enclosed in ```json code blocks.
        """
        
        for attempt in range(self.max_retries):
            try:
                gptmodel = self.get_gpt_4o_mini_model(temperature=0.7)
                response = gptmodel(extraction_prompt)
                
                # Extract JSON content
                if "```json" in response:
                    json_content = response.split("```json")[1].split("```")[0].strip()
                else:
                    json_content = response
                
                parsed_response = json.loads(json_content)
                
                # Validate expected keys exist
                if "competitors" not in parsed_response:
                    raise KeyError("Missing 'competitors' key in response")
                
                competitor_names = parsed_response.get("competitors", [])
                
                if not competitor_names or not isinstance(competitor_names, list):
                    self.env.add_system_log(f"No valid competitor names found, retrying ({attempt+1}/{self.max_retries})")
                    raise ValueError("Invalid competitor list format")
                
                # If we reach here, JSON is valid with expected structure
                break
                
            except (json.JSONDecodeError, KeyError, ValueError, IndexError) as e:
                self.env.add_system_log(f"JSON parsing error in competitor extraction: {str(e)}")
                if attempt == self.max_retries - 1:
                    self.env.add_system_log("Maximum retries reached, using fallback approach")
                    # Fallback: Ask the model to extract just the names directly
                    fallback_prompt = f"""
                        The previous extraction failed. From the following competitor data:
                        {competitors_data}
                        
                        Please list ONLY the company names of competitors, one per line.
                        Don't include any other information or formatting.
                    """
                    fallback_response = self.get_gpt_4o_mini_model(temperature=0.3)(fallback_prompt)
                    competitor_names = [name.strip() for name in fallback_response.split('\n') if name.strip()]
                    break
        
        result = {
            "direct_competitors": [],
            "indirect_competitors": []
        }
        
        for name in competitor_names:
            self.env.add_system_log(f"Getting competitor details for: {name}")
            competitor_info = self._get_competitor_details(name, company_info)
            if competitor_info:
                try:
                    # Process competitor info
                    processed_info = self._process_competitor_json(competitor_info, name)
                    if processed_info:
                        category = "direct_competitors" if processed_info.get("is_direct", False) else "indirect_competitors"
                        result[category].append(processed_info)
                except Exception as e:
                    self.env.add_system_log(f"Error processing competitor info for {name}: {str(e)}")
        
        return result
    
    def _process_competitor_json(self, competitor_json, competitor_name):
        """
        Process and validate competitor JSON data
        
        Args:
            competitor_json (str): JSON string with competitor data
            competitor_name (str): Name of the competitor
            
        Returns:
            dict: Processed and validated competitor data
        """
        for attempt in range(self.max_retries):
            try:
                # Extract JSON content
                if "```json" in competitor_json:
                    json_content = competitor_json.split("```json")[1].split("```")[0].strip()
                else:
                    json_content = competitor_json
                
                data = json.loads(json_content)
                
                # Validate required keys
                required_sections = ["companyProfile", "description", "comparisons", "is_direct"]
                for section in required_sections:
                    if section not in data:
                        raise KeyError(f"Missing required section: {section}")
                
                if "similarities" not in data["comparisons"] or "differences" not in data["comparisons"]:
                    raise KeyError("Missing similarities or differences in comparisons")
                
                # Valid JSON with all required keys
                return data
                
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                self.env.add_system_log(f"Error processing JSON for {competitor_name}: {str(e)}, attempt {attempt+1}/{self.max_retries}")
                
                if attempt == self.max_retries - 1:
                    # Create standardized structure if all retries fail
                    self.env.add_system_log(f"Creating fallback structure for {competitor_name}")
                    return self._create_fallback_competitor_structure(competitor_name, competitor_json)
        
        return None
    
    def _create_fallback_competitor_structure(self, competitor_name, raw_data):
        """
        Create a fallback structure when JSON parsing fails
        
        Args:
            competitor_name (str): Name of the competitor
            raw_data (str): Raw text data about the competitor
            
        Returns:
            dict: Standardized competitor structure
        """
        fallback_prompt = f"""
            I need to structure information about competitor "{competitor_name}" into a specific JSON format.
            The previous parsing attempts failed. 
            
            Here's the raw information I have:
            {raw_data}
            
            Please create a clean, valid JSON object with this exact structure:
            {{
                "companyProfile": {{
                    "name": "{competitor_name}",
                    "yearFounded": "YEAR or Unknown if not available",
                    "headquarters": "LOCATION or Unknown if not available",
                    "website": "URL or Unknown if not available",
                    "fundingStage": "STAGE or Unknown if not available",
                    "lastFundedAmount": "AMOUNT or Unknown if not available",
                    "totalFundsRaised": "AMOUNT or Unknown if not available",
                    "lastValuation": "AMOUNT or Unknown if not available",
                    "investors": ["Unknown if not available"]
                }},
                "description": "Brief description of the company",
                "comparisons": {{
                    "similarities": ["At least one similarity"],
                    "differences": ["At least one difference"]
                }},
                "is_direct": true or false
            }}
            
            Your response must be ONLY valid JSON without any code block markers or other text.
        """
        
        try:
            gptmodel = self.get_gpt_4o_mini_model(temperature=0.5)
            fallback_response = gptmodel(fallback_prompt)
            
            # Handle potential JSON formatting
            if "```json" in fallback_response:
                json_content = fallback_response.split("```json")[1].split("```")[0].strip()
            elif "```" in fallback_response:
                json_content = fallback_response.split("```")[1].strip()
            else:
                json_content = fallback_response.strip()
            
            parsed_fallback = json.loads(json_content)
            self.env.add_system_log(f"Successfully created fallback structure for {competitor_name}")
            return parsed_fallback
            
        except Exception as e:
            self.env.add_system_log(f"Fallback creation failed for {competitor_name}: {str(e)}")
            # Last resort: return minimal valid structure
            return {
                "companyProfile": {
                    "name": competitor_name,
                    "yearFounded": "Unknown",
                    "headquarters": "Unknown",
                    "website": "Unknown",
                    "fundingStage": "Unknown",
                    "lastFundedAmount": "Unknown",
                    "totalFundsRaised": "Unknown",
                    "lastValuation": "Unknown",
                    "investors": ["Unknown"]
                },
                "description": f"Information about {competitor_name} could not be properly structured.",
                "comparisons": {
                    "similarities": ["Information unavailable"],
                    "differences": ["Information unavailable"]
                },
                "is_direct": False
            }
    
    def _get_competitor_details(self, competitor_name, original_company_info):
        """
        Get detailed information about a specific competitor
        
        Args:
            competitor_name (str): Name of the competitor
            original_company_info (str): Information about the original company
            
        Returns:
            str: JSON string with competitor details
        """
        # STEP 1: Search for information using web search
        search_prompt = f"""
            Search for detailed information about {competitor_name} and compare it with this company:
            {original_company_info}
            
            Include the following details about {competitor_name}:
            - Year founded
            - Headquarters location
            - Company website
            - Funding stage
            - Last funded amount
            - Total funds raised
            - Last valuation (if available)
            - Key investors
            - Main products or services
            - Target market
            - Comparison with the original company
            
            Please provide comprehensive information about all these aspects.
        """
        
        try:
            # First call: With web search enabled
            search_response = self.client.chat.completions.create(
                model="gpt-4o-search-preview",
                web_search_options={},
                messages=[{"role": "user", "content": search_prompt}],
            )
            
            # Get the detailed information from the search
            detailed_info = search_response.choices[0].message.content
            
            # STEP 2: Parse the information into structured JSON
            parse_prompt = f"""
                Based on this detailed information about {competitor_name}:
                
                {detailed_info}
                
                Create a structured comparison with the original company:
                {original_company_info}
                
                Return ONLY a JSON object with EXACTLY this structure:
                {{
                    "companyProfile": {{
                        "name": "{competitor_name}",
                        "yearFounded": "YEAR",
                        "headquarters": "LOCATION",
                        "website": "URL",
                        "fundingStage": "STAGE",
                        "lastFundedAmount": "AMOUNT",
                        "totalFundsRaised": "AMOUNT",
                        "lastValuation": "AMOUNT",
                        "investors": ["INVESTOR1", "INVESTOR2"]
                    }},
                    "description": "DESCRIPTION",
                    "comparisons": {{
                        "similarities": ["SIMILARITY1", "SIMILARITY2", "SIMILARITY3"],
                        "differences": ["DIFFERENCE1", "DIFFERENCE2", "DIFFERENCE3"]
                    }},
                    "is_direct": true/false
                }}
                
                Ensure you include at least 3 specific similarities and 3 specific differences.
                The "is_direct" field should be true if {competitor_name} competes directly with the original company.
                Your response must be valid JSON enclosed in ```json code blocks.
            """
            
            gptmodel = self.get_gpt_4o_mini_model(temperature=0.7)
            parse_response = gptmodel(parse_prompt)
            
            return parse_response
            
        except Exception as e:
            self.env.add_system_log(f"Error getting competitor details for {competitor_name}: {str(e)}")
            return None
    
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
        shared["competitors"] = exec_res
        total_direct = len(exec_res.get("direct_competitors", []))
        total_indirect = len(exec_res.get("indirect_competitors", []))
        
        print(f"Found {total_direct} direct competitors and {total_indirect} indirect competitors.")
        return "default"