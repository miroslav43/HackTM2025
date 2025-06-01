import os
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_KEY")
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")

def load_system_prompt():
    """Load the system prompt from robust_prompts.txt file"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to src directory, then to instructions/robust_improved_user_querry
        prompts_path = os.path.join(script_dir, "..", "instructions", "robust_improved_user_querry", "robust_prompts.txt")
        prompts_path = os.path.normpath(prompts_path)
        
        with open(prompts_path, "r", encoding="utf-8") as file:
            system_prompt = file.read().strip()
            # Replace the date placeholder with current date
            system_prompt = system_prompt.replace("{CURRENT_DATE}", CURRENT_DATE)
            return system_prompt
    except FileNotFoundError:
        print(f"❌ Error: robust_prompts.txt file not found at {prompts_path}")
        print("Expected location: src/instructions/robust_improved_user_querry/robust_prompts.txt")
        return None
    except Exception as e:
        print(f"❌ Error loading system prompt: {e}")
        return None

def test_gemini_reformulation(
    user_query: str, 
    temperature: float = 0.1, 
    max_tokens: int = 1000,
    model: str = "gemini-2.0-flash"
) -> str:
    """
    Test Gemini API with the robust prompts system prompt
    
    Args:
        user_query: The user's query to be reformulated
        temperature: Controls randomness (0.0-1.0, lower = more focused)
        max_tokens: Maximum tokens to generate
        model: Gemini model to use (gemini-2.0-flash, gemini-2.5-flash-preview-05-20, etc.)
    
    Returns:
        The reformulated query from Gemini
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
    
    # Configure Gemini API
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Gemini API configured successfully")
    except Exception as e:
        print(f"❌ Error configuring Gemini API: {e}")
        return None
    
    print(f"\n🔧 Configuration:")
    print(f"   Model: {model}")
    print(f"   Temperature: {temperature}")
    print(f"   Max Tokens: {max_tokens}")
    print(f"   Current Date: {CURRENT_DATE}")
    print(f"\n📝 User Query: '{user_query}'")
    print(f"\n🤖 Processing with system prompt...")
    
    try:
        # Initialize the model
        model_instance = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt
        )
        
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        # Make API call
        response = model_instance.generate_content(
            user_query,
            generation_config=generation_config
        )
        
        # Extract response text
        if response and response.text:
            return response.text
        else:
            print("⚠️ No text found in response")
            return "No text found in response"
        
    except Exception as e:
        print(f"❌ Error making API call: {e}")
        return None

if __name__ == "__main__":
    print("=" * 80)
    print("GEMINI API TEST - ROBUST QUERY REFORMULATION")
    print("=" * 80)
    
    # Test configuration - you can modify these
    TEST_TEMPERATURE = 0.1  # Lower = more focused, Higher = more creative
    TEST_MAX_TOKENS = 500   # Adjust based on expected response length
    
    # Test query - modify this to test different queries
    TEST_QUERY = "taxe locuinta Timisoara"
    #"buletin nou copil 14 ani tm"
    
    # Additional test queries you can try (uncomment one):
    # TEST_QUERY = "Taxe locuinta 2025 Timisoara"
    # TEST_QUERY = "parcare centru"
    # TEST_QUERY = "ajutor pt firma mica"
    # TEST_QUERY = "pasaport nou"
    # TEST_QUERY = "inmatriculare auto second hand"
    
    print(f"🎯 Testing with query: '{TEST_QUERY}'")
    print("-" * 80)
    
    # Run the test
    result = test_gemini_reformulation(
        user_query=TEST_QUERY,
        temperature=TEST_TEMPERATURE,
        max_tokens=TEST_MAX_TOKENS
    )
    
    if result:
        print("\n✅ REFORMULATED QUERY:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        print(f"\n📊 Response length: {len(result)} characters")
        print(f"📊 Estimated tokens: ~{len(result.split())}")
    else:
        print("\n❌ Failed to get response from Gemini")
    
    print("\n" + "=" * 80)
    print("Test completed. Modify TEST_QUERY, TEST_TEMPERATURE, or TEST_MAX_TOKENS to try different configurations.")
