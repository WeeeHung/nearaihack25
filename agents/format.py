markdown = None

##################### Layer 1 : Screening #####################

market_analysis_json = {
        "industry_overview": {
          "description": "",
          "size": "",
          "growth_rate": "",
          "trends": [],
          "regulations": ""
        },
        "target_audience": {
          "customer_segments": [],
          "customer_needs": "",
          "geography": []
        },
        "market_opportunity": {
          "problem_statement": "",
          "solution": "",
          "value_proposition": "",
          "traction": {
            "current_customers": "",
            "growth_rate": "",
            "key_partners": []
          }
        }
      }

team_evaluation_json = {
        "founders": {
          "founder_name": "",
          "background": "",
          "role": "",
          "compensation": ""
        },
        "key_team_members": [
          {
            "name": "",
            "role": "",
            "experience": "",
            "compensation": "",
            "hiring_strategy": ""
          }
        ],
        "organizational_structure": {
          "management_layer": "",
          "advisory_board": ""
        }
      }

financial_json = {
        "revenue_model": {
          "business_model": "",
          "pricing": "",
          "revenue_streams": []
        },
        "historical_financials": {
          "revenue": {
            "year_1": "",
            "year_2": "",
            "year_3": ""
          },
          "profits": {
            "year_1": "",
            "year_2": "",
            "year_3": ""
          },
          "expenses": {
            "cost_of_goods_sold": "",
            "operating_expenses": ""
          }
        },
        "financial_projections": {
          "next_3_years": {
            "projected_revenue": "",
            "projected_profit": "",
            "break_even_analysis": ""
          },
          "funding_needs": ""
        },
        "investments": {
          "current_investors": [],
          "capital_raised": "",
          "equity_ownership": {
            "founders": "",
            "investors": ""
          }
        }
      }

tech_deep_dive_json = {
        "company_name": "",
        "architecture": {
            "stack": [],
            "architecture_type": "",
            "infrastructure": "",
            "scalability_assessment": "",
            "security_assessment": "",
            "technical_debt": ""
        },
        "technical_differentiation": {
            "differentiators": [
                {
                    "name": "",
                    "description": "",
                    "advantage_level": "",  # Low/Medium/High
                    "sustainability": ""
                }
            ]
        },
        "team_technical_assessment": {
            "technical_expertise_match": "",  # Low/Medium/High
            "technical_leadership": "",
            "key_strengths": [],
            "gaps": [],
            "risk_assessment": ""
        },
        "engineering_factors": {
            "factors": [
                {
                    "name": "",
                    "assessment": "",
                    "impact": ""  # Low/Medium/High
                }
            ]
        },
        "summary": {
            "executive_summary": "",
            "strengths": [],
            "risks": [],
            "viability_rating": "",  # Low/Medium/High
            "recommendations": []
        }
}

legal_json = {
        "corporate_structure": {
          "company_type": "",
          "jurisdiction": ""
        },
        "contracts_and_agreements": {
          "partnerships": "",
          "supplier_contracts": "",
          "customer_agreements": ""
        },
        "compliance_and_regulations": {
          "industry_regulations": "",
          "data_protection": ""
        }
      }

competition_json = {
    "companyProfile": {
        "name": "",
        "yearFounded": "",
        "headquarters": "",
        "website": "",
        "fundingStage": "",
        "lastFundedAmount": "",
        "totalFundsRaised": "",
        "lastValuation": "",
        "investors": []
    },
    "description": "",
    "comparisons": {
        "similarities": [],
        "differences": []
    },
    "is_direct": False
}


output_format_screening = {
      "market_analysis": market_analysis_json,
      "team_data": team_evaluation_json,
      "financial": financial_json,
      "company_info": tech_deep_dive_json,
      "legal": legal_json,
      "competition": competition_json
    }

  
# ######################## Layer 2.1 : Market Analysis #########################

# input_format = output_format_screening
# # outputs 
# output_format_market_analysis = {}

# ######################## Layer 2.2 : Team Evaluation #########################

# input_format = output_format_screening
# output_format_team_evaluation = {}
      

# ######################## Layer 3.1 : Financial #########################

# input_format = output_format_market_analysis 
# + financial_json
# output_format_financial = markdown


# ######################## Layer 3.2 : Tech Deep Dive #########################

# input_format = output_format_market_analysis 
# + output_format_team_evaluation 
# + tech_deep_dive_json
# output_format_tech_deep_dive = markdown


# ######################## Layer 3.3 : Legal #########################

# input_format = output_format_market_analysis 
# + legal_json
# output_format_legal = markdown


# ######################## Layer 3.4 : Risk #########################

# input_format = output_format_market_analysis 
# + output_format_team_evaluation
# output_format_risk = markdown


# ######################## Layer 3.5 : Competition #########################

# input_format = output_format_market_analysis 
# + competition_json
# output_format_competition = markdown

# ######################## Layer 4 : Final Output #########################

# input_format = output_format_market_analysis 
# + output_format_team_evaluation 
# + output_format_financial 
# + output_format_tech_deep_dive 
# + output_format_legal 
# + output_format_competition 
# + output_format_risk

# output_format_final = markdown
