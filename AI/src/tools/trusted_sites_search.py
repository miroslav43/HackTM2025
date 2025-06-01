import os
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
import json
import requests
import re

# Load environment variables
load_dotenv()

# Get API keys from environment
GEMINI_API_KEY = os.getenv("GEMINI_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")

def load_system_prompt():
    """Load the system prompt from trusted_sites.txt file"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to src directory, then to instructions/trusted_sites
        prompts_path = os.path.join(script_dir, "..", "instructions", "trusted_sites", "trusted_sites.txt")
        prompts_path = os.path.normpath(prompts_path)
        
        with open(prompts_path, "r", encoding="utf-8") as file:
            system_prompt = file.read().strip()
            # Replace the date placeholder with current date
            system_prompt = system_prompt.replace("{CURRENT_DATE}", CURRENT_DATE)
            return system_prompt
    except FileNotFoundError:
        print(f"❌ Error: trusted_sites.txt file not found at {prompts_path}")
        print("Expected location: src/instructions/trusted_sites/trusted_sites.txt")
        return None
    except Exception as e:
        print(f"❌ Error loading system prompt: {e}")
        return None

def load_search_system_prompt():
    """Load the system prompt for web search from system_prompt_search.txt file"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to src directory, then to instructions/trusted_sites
        prompts_path = os.path.join(script_dir, "..", "instructions", "trusted_sites", "system_prompt_search.txt")
        prompts_path = os.path.normpath(prompts_path)
        
        with open(prompts_path, "r", encoding="utf-8") as file:
            system_prompt = file.read().strip()
            # Replace the date placeholder with current date
            system_prompt = system_prompt.replace("{CURRENT_DATE}", CURRENT_DATE)
            return system_prompt
    except FileNotFoundError:
        print(f"❌ Error: system_prompt_search.txt file not found at {prompts_path}")
        print("Expected location: src/instructions/trusted_sites/system_prompt_search.txt")
        return None
    except Exception as e:
        print(f"❌ Error loading search system prompt: {e}")
        return None

def validate_and_extract_domains(response_text):
    """
    Validate that the response contains a proper JSON array of domains
    Returns the list of domains if valid, None otherwise
    """
    if not response_text:
        return None
    
    try:
        # Try to parse the entire response as JSON first
        response_text = response_text.strip()
        if response_text.startswith('[') and response_text.endswith(']'):
            domains = json.loads(response_text)
            if isinstance(domains, list) and all(isinstance(d, str) for d in domains):
                print(f"✅ Valid JSON array found with {len(domains)} domains")
                return domains
        
        # If that fails, try to extract JSON from text using regex
        json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
        if json_match:
            domains = json.loads(json_match.group())
            if isinstance(domains, list) and all(isinstance(d, str) for d in domains):
                print(f"✅ Extracted valid JSON array with {len(domains)} domains from text")
                return domains
        
        print("❌ Response does not contain a valid JSON array of domains")
        return None
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error validating domains: {e}")
        return None

def test_gemini_domain_selection(
    user_query: str, 
    temperature: float = 0.1, 
    max_tokens: int = 1000,
    model: str = "gemini-2.5-flash-preview-05-20"
) -> dict:
    """
    Test Gemini 2.5 Flash for domain selection using the older library syntax
    
    Args:
        user_query: The user's query for which to select relevant domains
        temperature: Controls randomness (0.0-1.0, lower = more focused)
        max_tokens: Maximum tokens to generate
        model: Gemini model to use
    
    Returns:
        Dict containing the domain list and metadata
    """
    
    # Validate API key
    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_KEY not found in environment variables")
        print("Please check your .env file and ensure GEMINI_KEY is set")
        return None
    
    # Load system prompt
    system_prompt = load_system_prompt()
    if not system_prompt:
        return None
    
    print(f"\n🔧 Gemini Configuration:")
    print(f"   Model: {model}")
    print(f"   Temperature: {temperature}")
    print(f"   Max Tokens: {max_tokens}")
    print(f"   Current Date: {CURRENT_DATE}")
    print(f"\n📝 User Query: '{user_query}'")
    print(f"\n🤖 Processing domain selection...")
    
    try:
        # Configure Gemini API using older syntax
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Gemini API configured successfully")
        
        # Configure safety settings to prevent blocking
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        # Initialize the model using older syntax
        model_instance = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt + "\n\n**IMPORTANT: Răspundeți DOAR cu o listă JSON de domenii (format array), de exemplu: [\"dfmt.ro\",\"servicii.primariatm.ro\",\"primariatm.ro\"]. Nu includeți text explicativ sau analiză - doar lista JSON.**",
            safety_settings=safety_settings
        )
        
        # Configure generation parameters using older syntax
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        print(f"🔧 Making API call to {model}...")
        
        # Make API call using older syntax
        response = model_instance.generate_content(
            user_query,
            generation_config=generation_config
        )
        
        print(f"📨 Response received, processing...")
        
        # Initialize result structure
        result = {
            "domains": None,
            "raw_response": None,
            "usage_metadata": {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0
            }
        }
        
        # Better error handling for blocked responses
        if response and hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            
            # Check if the response was blocked
            if hasattr(candidate, 'finish_reason'):
                finish_reason = candidate.finish_reason
                if finish_reason == 2:  # SAFETY
                    print(f"⚠️ Response was blocked due to safety filters")
                    print(f"📝 Attempting simplified query...")
                    # Try with a simplified, more direct query
                    simplified_query = f"Pentru query-ul despre '{user_query[:50]}', returnează o listă JSON cu domeniile oficiale românești relevante."
                    response = model_instance.generate_content(
                        simplified_query,
                        generation_config=generation_config
                    )
        
        # Extract response text
        if response and response.text:
            result["raw_response"] = response.text
            print(f"✅ Response extracted: {len(response.text)} characters")
            
            # Extract usage metadata if available
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = response.usage_metadata
                result["usage_metadata"] = {
                    "total_tokens": getattr(usage, 'total_token_count', 0),
                    "input_tokens": getattr(usage, 'prompt_token_count', 0),
                    "output_tokens": getattr(usage, 'candidates_token_count', 0)
                }
                print(f"📊 Token usage: {result['usage_metadata']['total_tokens']} total tokens")
            
            # Validate and extract domains from response
            domains = validate_and_extract_domains(result["raw_response"])
            result["domains"] = domains
            
            if not domains:
                print(f"⚠️ Could not extract valid domain list from response")
                print(f"Raw response: {result['raw_response'][:500]}...")  # Show first 500 chars
        else:
            print(f"❌ No response text found or response was blocked")
            # If we still can't get a response, return a default list of domains
            print(f"📋 Using fallback domain list for parking-related queries")
            fallback_domains = ["primariatm.ro", "timpark.ro", "servicii.primariatm.ro"]
            result["domains"] = fallback_domains
            result["raw_response"] = f"Fallback domains used due to API response issue: {fallback_domains}"
        
        return result
        
    except Exception as e:
        print(f"❌ Error making Gemini API call: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

def search_with_perplexity_filtered(
    query: str,
    domain_filter: list,
    city_hint: str = "timisoara",
    model: str = "sonar-reasoning-pro",
    temperature: float = 0.1,
    max_tokens: int = 10000,
    search_context_size: str = "high",
    search_after_date: str = "1/1/2005",
    search_before_date: str = "5/30/2025"
) -> str:
    """
    Search with Perplexity API using domain filter from Gemini selection
    
    Args:
        query: The user's search query
        domain_filter: List of domains to search (from Gemini selection)
        city_hint: City context for location filtering
        model: Perplexity model to use
        temperature: Controls randomness
        max_tokens: Maximum tokens for response
        search_context_size: Search context size (low/medium/high)
        search_after_date: Search after this date (M/D/YYYY format)
        search_before_date: Search before this date (M/D/YYYY format)
    
    Returns:
        The search results from Perplexity
    """
    
    if not PERPLEXITY_API_KEY:
        print("❌ Error: PERPLEXITY_API_KEY not found in environment variables")
        return None
    
    # Load search system prompt
    search_system_prompt = load_search_system_prompt()
    if not search_system_prompt:
        return None
    
    # Location filter for Romania with city hint
    location_filter = {"country": "RO", "city": city_hint}
    
    print(f"\n🔧 Perplexity Configuration:")
    print(f"   Model: {model}")
    print(f"   Temperature: {temperature}")
    print(f"   Max Tokens: {max_tokens}")
    print(f"   Context Size: {search_context_size}")
    print(f"   Search Date Range: {search_after_date} - {search_before_date}")
    print(f"   Location Filter: {city_hint}, Romania")
    print(f"   Domain Filter: {len(domain_filter)} domains")
    print(f"\n📍 Searching in filtered domains: {domain_filter}")
    print(f"🔍 Query: {query}")
    
    # Prepare request headers
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare request payload with domain filter
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": search_system_prompt
            },
            {
                "role": "user", 
                "content": query
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "search_after_date_filter": search_after_date,
        "search_before_date_filter": search_before_date,
        "search_domain_filter": domain_filter,  # This is the key addition
        "web_search_options": {
            "user_location": location_filter,
            "search_context_size": search_context_size
        }
    }
    
    try:
        print("🌐 Making Perplexity API call with domain filter...")
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data and response_data.get("choices") and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                print("✅ Perplexity search completed successfully!")
                return content
            else:
                print("⚠️ No valid response received from Perplexity")
                return None
        else:
            print(f"❌ Perplexity API Error - Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error calling Perplexity API: {e}")
        return None

def save_results_to_file(user_query, domains, search_results, gemini_metadata, filename=None):
    """Save the complete workflow results to a file"""
    if filename is None:
        # Create filename from query
        clean_query = re.sub(r'[^\w\s-]', '', user_query)
        clean_query = re.sub(r'\s+', '_', clean_query)
        clean_query = clean_query[:50].strip('_')
        timestamp = datetime.now().strftime("%m_%d_%H_%M")
        filename = f"{clean_query}_{timestamp}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write("="*80 + "\n")
            file.write("TRUSTED SITES SEARCH - GEMINI + PERPLEXITY INTEGRATION\n")
            file.write("="*80 + "\n\n")
            file.write(f"Original Query: {user_query}\n")
            file.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write("-"*80 + "\n\n")
            
            file.write("STEP 1: DOMAIN SELECTION WITH GEMINI 2.5 FLASH\n")
            file.write("-"*50 + "\n")
            file.write(f"Selected Domains ({len(domains)} total):\n")
            for i, domain in enumerate(domains, 1):
                file.write(f"   {i}. {domain}\n")
            file.write(f"\nGemini Token Usage:\n")
            file.write(f"   Total Tokens: {gemini_metadata['total_tokens']}\n")
            file.write(f"   Input Tokens: {gemini_metadata['input_tokens']}\n")
            file.write(f"   Output Tokens: {gemini_metadata['output_tokens']}\n")
            
            file.write("\n" + "-"*80 + "\n\n")
            file.write("STEP 2: WEB SEARCH WITH PERPLEXITY (DOMAIN FILTERED)\n")
            file.write("-"*50 + "\n")
            file.write("Search Configuration:\n")
            file.write(f"   - Domain Filter: {len(domains)} Romanian trusted sites\n")
            file.write("   - Geographic Filter: Romania\n")
            file.write("   - Date Filter: 2005-2025\n")
            file.write("   - Model: sonar-reasoning-pro\n\n")
            
            file.write("SEARCH RESULTS:\n")
            file.write("-"*20 + "\n")
            file.write(search_results or "No results obtained")
            
            file.write("\n\n" + "="*80 + "\n")
            file.write("WORKFLOW SUMMARY:\n")
            file.write("1. User query analyzed by Gemini 2.5 Flash thinking model\n")
            file.write("2. Most relevant Romanian government sites selected\n")
            file.write("3. Perplexity search restricted to selected domains only\n")
            file.write("4. Results formatted as step-by-step instructions\n")
            file.write("="*80 + "\n")
        
        print(f"💾 Results saved to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving results: {e}")
        return None

def integrated_trusted_sites_search(
    user_query: str,
    # Gemini parameters
    gemini_temperature: float = 0.1,
    gemini_max_tokens: int = 2000,
    gemini_model: str = "gemini-2.5-flash-preview-05-20",
    # Perplexity parameters
    perplexity_model: str = "sonar-reasoning-pro",
    perplexity_temperature: float = 0.1,
    perplexity_max_tokens: int = 10000,
    city_hint: str = "timisoara",
    search_context_size: str = "high",
    search_after_date: str = "1/1/2005",
    search_before_date: str = "5/30/2025",
    # Output parameters
    save_to_file: bool = True
) -> dict:
    """
    Complete integrated workflow: Domain selection with Gemini + Web search with Perplexity
    
    Returns:
        Dict containing all results and metadata from both steps
    """
    
    print("🚀 Starting Integrated Trusted Sites Search")
    print("="*60)
    
    # Step 1: Domain Selection with Gemini
    print("\n📋 STEP 1: Domain Selection with Gemini 2.5 Flash")
    print("-"*50)
    
    gemini_result = test_gemini_domain_selection(
        user_query=user_query,
        temperature=gemini_temperature,
        max_tokens=gemini_max_tokens,
        model=gemini_model
    )
    
    if not gemini_result or not gemini_result.get("domains"):
        print("❌ Domain selection failed. Cannot proceed with search.")
        return {"success": False, "error": "Domain selection failed"}
    
    domains = gemini_result["domains"]
    print(f"\n✅ Domain selection completed: {len(domains)} domains selected")
    
    # Step 2: Web Search with Perplexity
    print("\n🔍 STEP 2: Web Search with Perplexity (Domain Filtered)")
    print("-"*50)
    
    search_results = search_with_perplexity_filtered(
        query=user_query,
        domain_filter=domains,
        city_hint=city_hint,
        model=perplexity_model,
        temperature=perplexity_temperature,
        max_tokens=perplexity_max_tokens,
        search_context_size=search_context_size,
        search_after_date=search_after_date,
        search_before_date=search_before_date
    )
    
    if not search_results:
        print("❌ Web search failed.")
        return {
            "success": False, 
            "error": "Web search failed",
            "domains": domains,
            "gemini_result": gemini_result
        }
    
    print(f"\n✅ Web search completed successfully!")
    
    # Step 3: Save Results
    filename = None
    if save_to_file:
        print("\n💾 STEP 3: Saving Results")
        print("-"*50)
        filename = save_results_to_file(
            user_query=user_query,
            domains=domains,
            search_results=search_results,
            gemini_metadata=gemini_result["usage_metadata"]
        )
    
    # Return complete results
    return {
        "success": True,
        "user_query": user_query,
        "selected_domains": domains,
        "search_results": search_results,
        "gemini_result": gemini_result,
        "output_file": filename,
        "workflow_completed": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

if __name__ == "__main__":
    print("=" * 80)
    print("INTEGRATED TRUSTED SITES SEARCH - GEMINI + PERPLEXITY")
    print("=" * 80)
    print("🔄 Complete Workflow:")
    print("   1️⃣  Gemini 2.5 Flash selects most relevant Romanian government domains")
    print("   2️⃣  Perplexity searches only those selected domains") 
    print("   3️⃣  Results formatted as actionable instructions")
    print("=" * 80)
    
    # Test configuration - you can modify these
    TEST_QUERY = "Care sunt taxele și impozitele locale datorate pentru o locuință (casă sau apartament) în Timișoara, România în 2025, cum se calculează, unde se pot plăti online sau fizic, care sunt termenele limită de plată și ce facilități fiscale sunt disponibile pentru proprietari?"
    
    # Additional test queries you can try (uncomment one):
    # TEST_QUERY = "Cum imi reinoiesc buletinul"
    # TEST_QUERY = "parcare centru Timisoara"
    # TEST_QUERY = "ajutor social copii"
    # TEST_QUERY = "pasaport nou documentele necesare"
    # TEST_QUERY = "inmatriculare auto second hand"
    # TEST_QUERY = "plata online factura apa caldura"
    
    print(f"\n🎯 Testing integrated search for query: '{TEST_QUERY}'")
    print("-" * 80)
    
    # Run the integrated workflow
    result = integrated_trusted_sites_search(
        user_query=TEST_QUERY,
        # You can customize parameters here
        save_to_file=True
    )
    
    if result["success"]:
        print(f"\n🎉 INTEGRATED SEARCH COMPLETED SUCCESSFULLY!")
        print("-" * 60)
        print(f"✅ Domains selected: {len(result['selected_domains'])}")
        print(f"✅ Search results obtained: {len(result['search_results'])} characters")
        if result["output_file"]:
            print(f"✅ Results saved to: {result['output_file']}")
        print("\n📋 Selected Domains:")
        for i, domain in enumerate(result["selected_domains"], 1):
            print(f"   {i}. {domain}")
    else:
        print(f"\n❌ INTEGRATED SEARCH FAILED")
        print(f"Error: {result['error']}")
    
    print("\n" + "=" * 80)
    print("✨ Integration complete! This tool now combines:")
    print("   🧠 Gemini 2.5 Flash for domain selection")
    print("   🔍 Perplexity web search with domain filtering")
    print("   📝 Structured output with step-by-step instructions")
    print("   💾 Complete workflow documentation")
