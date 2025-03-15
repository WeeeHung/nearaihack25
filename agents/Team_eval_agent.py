import openai
import googlesearch
import requests
import json

from base_agent import BaseAgent

class TeamEvalAgent(BaseAgent):
    def __init__(self, name="TeamEvalAgent"):
        """
        Initialize the team evaluation agent with specific functionality.
        
        Args:
            name (str): Name of the agent
        """
        super().__init__(name)
        
        # Load API keys from environment variables
        self._load_api_keys()
        
        # Initialize OpenAI client
        self.client = openai.Client(api_key=self.api_keys.get("OPENAI_API_KEY"))

    def linkedin_scraper(self, team_members):
        """
        Collect LinkedIn profile information for each team member and extract 
        their experiences, education, and achievements.

        Args:
            team_members (list): List of names of the team members.
        
        Returns:
            dict: JSON-formatted data with team members' professional information.
        """
        linkedin_urls = {}
        
        print("Please enter the LinkedIn URLs for the following team members:")
        for member in team_members:
            url = input(f"LinkedIn URL for {member}: ").strip()
            linkedin_urls[member] = url

        print("\nFetching professional information for each team member...")
        team_data = {}
        
        for member, url in linkedin_urls.items():
            print(f"\nAnalyzing LinkedIn profile for {member}...")
            
            if not url or not url.startswith("http"):
                print(f"Skipping {member} - Invalid or missing LinkedIn URL")
                team_data[member] = {
                    "name": member,
                    "url": url,
                    "error": "Invalid or missing LinkedIn URL",
                    "experiences": [],
                    "education": [],
                    "achievements": []
                }
                continue
            
            try:
                # Use OpenAI to extract information from the LinkedIn profile
                prompt = f"""
                Tell me about this guy: {url}

                List his experiences, education, and achievements.
                """
                
                # Use the web-enabled GPT model to extract information
                response = self.client.chat.completions.create(
                    model="gpt-4o-search-preview",
                    web_search_options={},
                    messages=[{"role": "user", "content": prompt}],
                )
                
                extracted_info = response.choices[0].message.content
                
                # Parse the extracted information into structured JSON
                parse_prompt = f"""
                Based on this extracted information from {member}'s LinkedIn profile:
                
                {extracted_info}
                
                Create a structured JSON with exactly this format:
                {{
                    "name": "{member}",
                    "url": "{url}",
                    "experiences": [
                        {{
                            "company": "Company Name",
                            "title": "Job Title",
                            "duration": "Time Period",
                            "description": "Key responsibilities and achievements"
                        }}
                    ],
                    "education": [
                        {{
                            "institution": "School Name",
                            "degree": "Degree Type",
                            "fieldOfStudy": "Field",
                            "dates": "Time Period"
                        }}
                    ],
                    "achievements": [
                        "Achievement 1",
                        "Achievement 2"
                    ],
                    "skills": [
                        "Skill 1",
                        "Skill 2"
                    ]
                }}
                
                Return ONLY the JSON with no additional text.
                """
                
                # Use a smaller model for parsing the information into JSON
                model = self.get_4o_mini_model(temperature=0.2)
                json_response = model(parse_prompt)
                
                # Extract the JSON from the response
                if "```json" in json_response:
                    json_str = json_response.split("```json")[1].split("```")[0].strip()
                elif "```" in json_response:
                    json_str = json_response.split("```")[1].split("```")[0].strip()
                else:
                    json_str = json_response.strip()
                    
                profile_data = json.loads(json_str)
                team_data[member] = profile_data
                
                print(f"✓ Successfully extracted information for {member}")
                
            except Exception as e:
                print(f"Error processing {member}'s profile: {str(e)}")
                team_data[member] = {
                    "name": member,
                    "url": url,
                    "error": str(e),
                    "experiences": [],
                    "education": [],
                    "achievements": [],
                    "skills": []
                }
        
        print("\nProfile analysis complete!")
        
        # Save the data to a file for reference
        with open("team_profiles.json", "w") as f:
            json.dump(team_data, f, indent=2)
        print("Team data saved to team_profiles.json")
        
        return team_data

    def prep(self, shared):
        """
        Prepare data for execution. Extract the company information from shared store.
        
        Args:
            shared (dict): Shared data store
            
        Returns:
            str: Company information to search for team evaluation
        """
        return shared.get("company_info", "")
    
    def exec(self, company_info):
        """
        Execute a search for team evaluation using the OpenAI API.
        
        Args:
            company_info (str): Information about the company to evaluate the team for
        
        Returns:
            dict: Structured data about team evaluation
        """
        search_prompt = f"""
            {company_info}
            
            The above contains information of a company - part of which is the team info extracted from their data room.
            Using this, extract the team members' names and put them in a list.

            Return ONLY the list of names in a python list format.
        """
        
        gptmodel = self.get_4o_mini_model(temperature=0.7)
        founders = gptmodel(search_prompt)
        founders = founders.strip("[]").replace("'", "").replace(" ", "").split("```python")[1].split("```")[0].strip()
        founders = json.loads(founders)

        founder_info = self.linkedin_scraper(founders)

        structured_data = self._structure_team_eval_data(founder_info)

        return structured_data
    
    def _structure_team_eval_data(self, team_eval_data):
        """
        Structure team evaluation data and get detailed analysis
        Args:
            team_eval_data (str): Initial search results with team evaluation information
            company_info (str): Original company information
        Returns:
            dict: Structured team evaluation data
        """
        gptmodel = self.get_4o_mini_model(temperature=0.7)

        prompt = f"""
            {team_eval_data}
            The above contains a detailed analysis of a company's team.
            Help me structure the data into a JSON format following the below format:
            {{
                "name": "Name",
                "url": "URL",
                "experiences": [
                    {{
                        "company": "Company Name",
                        "title": "Job Title",
                        "duration": "Time Period",
                        "description": "Key responsibilities and achievements"
                    }}
                ],
                "education": [
                    {{
                        "institution": "School Name",
                        "degree": "Degree Type",
                        "fieldOfStudy": "Field",
                        "dates": "Time Period"
                    }}
                ],
                "achievements": [
                    "Achievement 1",
                    "Achievement 2"
                ],
                "skills": [
                    "Skill 1",
                    "Skill 2"
                ]
            }}  
        """

        response = gptmodel(prompt)

        return response


# Test the agent
if __name__ == "__main__":
    agent = TeamEvalAgent()
    company_info = "Founders: Wee Hung"
    result = agent.exec(company_info)
    
