import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv
import sys

# Add the tools directory to the path so we can import from it
tools_path = os.path.join(os.path.dirname(__file__), 'tools')
sys.path.append(tools_path)

# Import our modules from the tools directory
from robust_user_querries import test_gemini_reformulation
from perplexity_web_search import search_with_perplexity_romania
from trusted_sites_search import integrated_trusted_sites_search
from concatenate_web_searches_into_final_response import concatenate_web_searches_into_final_response
from timpark_payment_tool import create_timpark_payment_tool

# Load environment variables
load_dotenv()

class AgentConfig:
    """Configuration class for the Agent"""
    
    def __init__(self, config_file="agent_config.json"):
        # If relative path, make it relative to this file's directory
        if not os.path.isabs(config_file):
            config_file = os.path.join(os.path.dirname(__file__), config_file)
        
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file or create default"""
        default_config = {
            "query_processing": {
                "use_robust_reformulation": True,
                "gemini_temperature": 0.1,
                "gemini_max_tokens": 1000
            },
            "web_search": {
                "city_hint": "timisoara",
                "use_perplexity": True
            },
            "output": {
                "save_to_file": True,
                "output_folder": "results/agent_results",
                "include_reformulated_query": True,
                "include_search_results": True,
                "file_naming": {
                    "use_config_name": True,
                    "include_timestamp": True
                }
            },
            "current_test": {
                "question": "taxe locuinta Timisoara",
                "config_name": "default_agent_config"
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_configs(default_config, loaded_config)
            else:
                # Create default config file
                self.save_config(default_config)
                print(f"✅ Created default config file: {self.config_file}")
                return default_config
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            print("Using default configuration")
            return default_config
    
    def _merge_configs(self, default, loaded):
        """Recursively merge loaded config with default config"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config=None):
        """Save current configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def get(self, path, default=None):
        """Get config value using dot notation (e.g., 'query_processing.use_robust_reformulation')"""
        keys = path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

class Agent:
    """Main Agent class that orchestrates query reformulation and web search"""
    
    def __init__(self, config_file="agent_config.json"):
        self.config = AgentConfig(config_file)
        self.ensure_output_folder()
    
    def ensure_output_folder(self):
        """Create output folder if it doesn't exist"""
        output_folder = self.config.get("output.output_folder", "results/agent_results")
        
        # Make path relative to src directory if not absolute
        if not os.path.isabs(output_folder):
            output_folder = os.path.join(os.path.dirname(__file__), output_folder)
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
            print(f"✅ Created output folder: {output_folder}")
    
    def _create_filename(self, question, config_name, step="final"):
        """Create filename based on configuration"""
        output_folder = self.config.get("output.output_folder", "results/agent_results")
        
        # Make path relative to src directory if not absolute
        if not os.path.isabs(output_folder):
            output_folder = os.path.join(os.path.dirname(__file__), output_folder)
        
        # Base filename
        if self.config.get("output.file_naming.use_config_name", True):
            base_name = config_name
        else:
            # Clean question for filename
            clean_question = re.sub(r'[^\w\s-]', '', question)
            clean_question = re.sub(r'\s+', '_', clean_question)
            clean_question = clean_question[:50]  # Allow longer filenames for questions
            clean_question = clean_question.strip('_')
            base_name = clean_question if clean_question else "agent_query"
        
        # Add step if not final
        if step != "final":
            base_name += f"_{step}"
        
        # Add timestamp if configured - using shorter format MM_DD_HH_MM
        if self.config.get("output.file_naming.include_timestamp", True):
            now = datetime.now()
            timestamp = f"{now.month}_{now.day}_{now.hour}_{now.minute}"
            base_name += f"_{timestamp}"
        
        filename = f"{base_name}.txt"
        return os.path.join(output_folder, filename)
    
    def save_reformulated_query(self, original_question, reformulated_query, config_name):
        """Save the reformulated query to file"""
        if not self.config.get("output.include_reformulated_query", True):
            return None
        
        filename = self._create_filename(original_question, config_name, "reformulated")
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("="*80 + "\n")
                f.write("AGENT - QUERY REFORMULAT CU GEMINI\n")
                f.write("="*80 + "\n\n")
                f.write(f"Config folosit: {config_name}\n")
                f.write(f"Data procesării: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Reformulare activată: {self.config.get('query_processing.use_robust_reformulation')}\n")
                f.write(f"Temperature Gemini: {self.config.get('query_processing.gemini_temperature')}\n")
                f.write(f"Max Tokens Gemini: {self.config.get('query_processing.gemini_max_tokens')}\n")
                f.write("-"*80 + "\n\n")
                f.write(f"ÎNTREBAREA ORIGINALĂ:\n{original_question}\n\n")
                f.write(f"QUERY REFORMULAT:\n{reformulated_query}\n\n")
                f.write("="*80 + "\n")
            
            print(f"💾 Query reformulat salvat în: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Eroare la salvarea query-ului reformulat: {e}")
            return None
    
    def save_final_results(self, original_question, final_query, search_results, config_name, reformulated_filename=None):
        """Save the final results to file"""
        if not self.config.get("output.include_search_results", True):
            return None
        
        filename = self._create_filename(original_question, config_name, "final")
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("="*80 + "\n")
                f.write("AGENT - REZULTATE FINALE\n")
                f.write("="*80 + "\n\n")
                f.write(f"Config folosit: {config_name}\n")
                f.write(f"Data procesării: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-"*80 + "\n\n")
                f.write("CONFIGURAȚIA FOLOSITĂ:\n")
                f.write(f"• Reformulare Gemini: {self.config.get('query_processing.use_robust_reformulation')}\n")
                f.write(f"• Temperature: {self.config.get('query_processing.gemini_temperature')}\n")
                f.write(f"• Max Tokens: {self.config.get('query_processing.gemini_max_tokens')}\n")
                f.write(f"• City Hint: {self.config.get('web_search.city_hint')}\n")
                f.write(f"• Folosește Perplexity: {self.config.get('web_search.use_perplexity')}\n")
                f.write("-"*80 + "\n\n")
                f.write(f"ÎNTREBAREA ORIGINALĂ:\n{original_question}\n\n")
                f.write(f"QUERY FOLOSIT PENTRU CĂUTARE:\n{final_query}\n\n")
                if reformulated_filename:
                    f.write(f"Fișier cu query reformulat: {reformulated_filename}\n\n")
                f.write("-"*80 + "\n\n")
                f.write("REZULTATELE CĂUTĂRII:\n")
                f.write(search_results)
                f.write("\n\n" + "="*80 + "\n")
            
            print(f"💾 Rezultate finale salvate în: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Eroare la salvarea rezultatelor finale: {e}")
            return None
    
    def process_query(self, custom_question=None, config_name_override=None):
        """Process a query through the configured pipeline"""
        
        # Get question and config name
        question = custom_question or self.config.config.get("current_test", {}).get("question", "taxe locuinta Timisoara")
        config_name = config_name_override or self.config.config.get("current_test", {}).get("config_name", "agent_result")
        
        print(f"\n📝 Întrebare: '{question}'")
        print(f"⚙️ Config: {config_name}")
        
        # Initialize variables
        reformulated_query = None
        final_result = None
        
        # Step 1: Query reformulation (if enabled)
        query_for_search = question  # Default to original
        
        if self.config.config["query_processing"]["use_robust_reformulation"]:
            print(f"\n🔄 PASUL 1: Reformulare query cu Gemini")
            print("-" * 50)
            
            # Get Gemini configuration
            gemini_config = self.config.config["query_processing"]
            
            reformulated_query = test_gemini_reformulation(
                user_query=question,
                temperature=gemini_config.get("gemini_temperature", 0.1),
                max_tokens=gemini_config.get("gemini_max_tokens", 1000),
                model=gemini_config.get("gemini_model", "gemini-2.0-flash")
            )
            
            if reformulated_query:
                print(f"✅ Query reformulat cu succes!")
                query_for_search = reformulated_query
            else:
                print("⚠️ Reformularea a eșuat, se va folosi query-ul original")
        else:
            print(f"\n⏭️ PASUL 1: Reformulare dezactivată (se folosește query-ul original)")
        
        # Step 2: TimPark Payment Tool (if enabled)
        timpark_result = None
        if self.config.config.get("timpark_payment", {}).get("use_timpark_payment", False):
            print(f"\n💳 PASUL 2: Analiză intenție plată parcare TimPark")
            print("-" * 50)
            
            # Get TimPark configuration
            timpark_config = self.config.config["timpark_payment"]
            
            try:
                # Create and process with TimPark payment tool
                timpark_tool = create_timpark_payment_tool(timpark_config)
                timpark_result = timpark_tool.process(question)
                
                if timpark_result["tool_enabled"]:
                    print(f"✅ Tool TimPark procesat cu succes!")
                    print(f"   🎯 Intenție detectată: {'DA' if timpark_result['tool_activated'] else 'NU'}")
                    print(f"   ⏰ Durată extrasă: {timpark_result['duration']}")
                    print(f"   📝 Mesaj: {timpark_result['message']}")
                    
                    if timpark_result['tool_activated'] and 'automation_result' in timpark_result:
                        automation = timpark_result['automation_result']
                        if automation['success']:
                            print(f"   🚗 Automatizare executată cu succes!")
                        else:
                            print(f"   ❌ Automatizare eșuată: {automation['error']}")
                else:
                    print("⚠️ Tool-ul TimPark nu este activat în configurație")
                    
            except Exception as e:
                print(f"❌ Eroare la procesarea cu tool-ul TimPark: {e}")
                timpark_result = None
        else:
            print(f"\n⏭️ PASUL 2: Tool TimPark dezactivat")
        
        # Check if TimPark tool was activated - if yes, skip remaining steps
        timpark_activated = (timpark_result and 
                            timpark_result.get("tool_enabled", False) and 
                            timpark_result.get("tool_activated", False))
        
        if timpark_activated:
            print(f"\n🚗 TimPark Payment Tool a fost activat și executat!")
            print(f"⏭️ Sărind peste pașii 3, 4 și 5 (căutări web nu sunt necesare)")
            print("-" * 50)
            
            # Set skipped steps to appropriate messages
            final_result = "📋 Pasul sărit - TimPark Payment Tool a fost executat cu succes"
            trusted_sites_result = {"success": False, "skipped": True, "reason": "TimPark Payment Tool executat"}
            final_synthesized_response = "📋 Răspuns final sărit - automatizarea plății parcării a fost completată cu succes"
        else:
            # Continue with normal workflow
            
            # Step 3: Web search (if enabled)
            if self.config.config["web_search"]["use_perplexity"]:
                print(f"\n🔍 PASUL 3: Căutare web cu Perplexity")
                print("-" * 50)
                print(f"Query pentru căutare: '{query_for_search}'")
                
                # Get web search configuration
                web_config = self.config.config["web_search"]
                
                final_result = search_with_perplexity_romania(
                    query=query_for_search,
                    city_hint=web_config.get("city_hint", "timisoara"),
                    model=web_config.get("perplexity_model", "sonar-reasoning-pro"),
                    temperature=web_config.get("perplexity_temperature", 0.1),
                    max_tokens=web_config.get("perplexity_max_tokens", 10000),
                    search_context_size=web_config.get("search_context_size", "high"),
                    search_after_date=web_config.get("search_date_range", {}).get("search_after_date", "1/1/2005"),
                    search_before_date=web_config.get("search_date_range", {}).get("search_before_date", "5/30/2025")
                )
                
                if final_result:
                    print(f"✅ Căutare completată cu succes!")
                else:
                    print("⚠️ Căutarea a eșuat")
            else:
                print(f"\n⏭️ PASUL 3: Căutare web dezactivată")
                final_result = f"Căutare web dezactivată. Query procesat: {query_for_search}"
            
            # Step 4: Trusted sites search (if enabled)
            trusted_sites_result = None
            if self.config.config["trusted_sites_search"]["use_trusted_sites_search"]:
                print(f"\n🏛️ PASUL 4: Căutare pe site-uri românești de încredere")
                print("-" * 50)
                print(f"Query pentru căutare: '{query_for_search}'")
                
                # Get trusted sites search configuration
                trusted_config = self.config.config["trusted_sites_search"]
                gemini_config = trusted_config["gemini_domain_selection"]
                perplexity_config = trusted_config["perplexity_filtered_search"]
                
                try:
                    trusted_sites_result = integrated_trusted_sites_search(
                        user_query=query_for_search,
                        # Gemini parameters for domain selection
                        gemini_temperature=gemini_config.get("gemini_temperature", 0.1),
                        gemini_max_tokens=gemini_config.get("gemini_max_tokens", 2000),
                        gemini_model=gemini_config.get("gemini_model", "gemini-2.5-flash-preview-05-20"),
                        # Perplexity parameters for filtered search
                        perplexity_model=perplexity_config.get("perplexity_model", "sonar-reasoning-pro"),
                        perplexity_temperature=perplexity_config.get("perplexity_temperature", 0.1),
                        perplexity_max_tokens=perplexity_config.get("perplexity_max_tokens", 10000),
                        city_hint=perplexity_config.get("city_hint", "timisoara"),
                        search_context_size=perplexity_config.get("search_context_size", "high"),
                        search_after_date=perplexity_config.get("search_after_date", "1/1/2005"),
                        search_before_date=perplexity_config.get("search_before_date", "5/30/2025"),
                        # Output parameters
                        save_to_file=trusted_config.get("output", {}).get("save_to_file", True)
                    )
                    
                    if trusted_sites_result and trusted_sites_result.get("success"):
                        print(f"✅ Căutare pe site-uri de încredere completată!")
                        print(f"   📋 Domenii selectate: {len(trusted_sites_result.get('selected_domains', []))}")
                        print(f"   📄 Rezultate căutare: {len(str(trusted_sites_result.get('search_results', '')))}")
                        if trusted_sites_result.get('output_file'):
                            print(f"   💾 Fișier salvat: {trusted_sites_result.get('output_file')}")
                        
                        # Print results for inspection
                        print(f"\n📊 REZULTATE TRUSTED SITES SEARCH:")
                        print("=" * 50)
                        print(f"Domenii selectate: {trusted_sites_result.get('selected_domains', [])}")
                        print(f"\nRezultat căutare (primele 500 caractere):")
                        search_text = str(trusted_sites_result.get('search_results', ''))
                        print(search_text[:500] + "..." if len(search_text) > 500 else search_text)
                        print("=" * 50)
                    else:
                        print("⚠️ Căutarea pe site-uri de încredere a eșuat")
                        if trusted_sites_result:
                            print(f"   Error: {trusted_sites_result.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"❌ Eroare la căutarea pe site-uri de încredere: {e}")
                    trusted_sites_result = None
            else:
                print(f"\n⏭️ PASUL 4: Căutare pe site-uri de încredere dezactivată")
            
            # Step 5: Final Response Generation (if enabled)
            final_synthesized_response = None
            if self.config.config["final_response_generation"]["use_final_response_generation"]:
                print(f"\n🎯 PASUL 5: Generare răspuns final sintetizat")
                print("-" * 50)
                
                # Get final response generation configuration
                final_config = self.config.config["final_response_generation"]
                
                try:
                    final_synthesized_response = concatenate_web_searches_into_final_response(
                        original_question=question,
                        reformulated_query=reformulated_query,
                        regular_web_search_results=final_result,
                        trusted_sites_search_results=trusted_sites_result,
                        # Gemini parameters
                        temperature=final_config.get("gemini_temperature", 0.1),
                        max_tokens=final_config.get("gemini_max_tokens", 15000),
                        model=final_config.get("gemini_model", "gemini-2.5-flash-preview-05-20"),
                        # RAG configuration parameters
                        rag_config=final_config.get("rag_context", {}),
                        # Output parameters
                        save_to_file=final_config.get("output", {}).get("save_to_file", True)
                    )
                    
                    if final_synthesized_response:
                        print(f"✅ Răspuns final generat cu succes!")
                        print(f"   📄 Lungime răspuns: {len(final_synthesized_response)} caractere")
                        
                        # Print preview of final response for inspection
                        print(f"\n📊 PREVIZUALIZARE RĂSPUNS FINAL:")
                        print("=" * 50)
                        preview = final_synthesized_response[:300] + "..." if len(final_synthesized_response) > 300 else final_synthesized_response
                        print(preview)
                        print("=" * 50)
                    else:
                        print("⚠️ Generarea răspunsului final a eșuat")
                except Exception as e:
                    print(f"❌ Eroare la generarea răspunsului final: {e}")
                    final_synthesized_response = None
            else:
                print(f"\n⏭️ PASUL 5: Generare răspuns final dezactivată")
        
        # Step 6: Save final results (if enabled)
        if self.config.config["output"]["save_to_file"] and self.config.config["output"]["include_search_results"]:
            print(f"\n💾 PASUL 6: Salvare rezultate finale")
            print("-" * 50)
            
            final_filename = self._create_filename(question, config_name)
            
            with open(final_filename, "w", encoding="utf-8") as f:
                if timpark_activated:
                    f.write(f"RAPORT AGENT - REZULTATE FINALE (TIMPARK PAYMENT EXECUTAT)\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"🚗 AUTOMATIZARE PLATĂ PARCARE EXECUTATĂ CU SUCCES!\n")
                    f.write(f"⏭️ Pașii 3, 4 și 5 au fost săriți deoarece plata a fost procesată.\n\n")
                else:
                    f.write(f"RAPORT AGENT - REZULTATE FINALE COMPLETE (5 INSTRUMENTE)\n")
                    f.write("=" * 60 + "\n\n")
                
                f.write(f"ÎNTREBARE ORIGINALĂ:\n{question}\n\n")
                
                if reformulated_query:
                    f.write(f"QUERY REFORMULAT:\n{reformulated_query}\n\n")
                
                f.write(f"CONFIGURAȚIA FOLOSITĂ:\n")
                f.write(f"- Config Name: {config_name}\n")
                f.write(f"- Reformulare activă: {self.config.config['query_processing']['use_robust_reformulation']}\n")
                f.write(f"- TimPark Payment Tool activ: {self.config.config.get('timpark_payment', {}).get('use_timpark_payment', False)}\n")
                
                if timpark_activated:
                    f.write(f"- PAȘII 3, 4, 5 SĂRIȚI: TimPark Payment Tool executat\n")
                else:
                    f.write(f"- Căutare web activă: {self.config.config['web_search']['use_perplexity']}\n")
                    f.write(f"- Căutare site-uri de încredere activă: {self.config.config['trusted_sites_search']['use_trusted_sites_search']}\n")
                    f.write(f"- Generare răspuns final activă: {self.config.config['final_response_generation']['use_final_response_generation']}\n")
                
                if self.config.config["query_processing"]["use_robust_reformulation"]:
                    f.write(f"- Model Gemini Reformulare: {self.config.config['query_processing'].get('gemini_model', 'gemini-2.0-flash')}\n")
                    f.write(f"- Temperature Gemini Reformulare: {self.config.config['query_processing'].get('gemini_temperature', 0.1)}\n")
                
                if self.config.config.get("timpark_payment", {}).get("use_timpark_payment", False):
                    f.write(f"- Model Gemini TimPark: {self.config.config['timpark_payment'].get('gemini_model', 'gemini-2.5-flash-preview-05-20')}\n")
                    f.write(f"- Temperature Gemini TimPark: {self.config.config['timpark_payment'].get('gemini_temperature', 0.1)}\n")
                
                if not timpark_activated:
                    if self.config.config["web_search"]["use_perplexity"]:
                        f.write(f"- Model Perplexity: {self.config.config['web_search'].get('perplexity_model', 'sonar-reasoning-pro')}\n")
                        f.write(f"- Temperature Perplexity: {self.config.config['web_search'].get('perplexity_temperature', 0.1)}\n")
                        f.write(f"- Context Size: {self.config.config['web_search'].get('search_context_size', 'high')}\n")
                    
                    if self.config.config["trusted_sites_search"]["use_trusted_sites_search"]:
                        f.write(f"- Model Gemini Trusted Sites: {self.config.config['trusted_sites_search']['gemini_domain_selection'].get('gemini_model', 'gemini-2.5-flash-preview-05-20')}\n")
                        f.write(f"- Model Perplexity Trusted Sites: {self.config.config['trusted_sites_search']['perplexity_filtered_search'].get('perplexity_model', 'sonar-reasoning-pro')}\n")
                    
                    if self.config.config["final_response_generation"]["use_final_response_generation"]:
                        f.write(f"- Model Gemini Final Response: {self.config.config['final_response_generation'].get('gemini_model', 'gemini-2.5-flash-preview-05-20')}\n")
                        f.write(f"- Temperature Final Response: {self.config.config['final_response_generation'].get('gemini_temperature', 0.1)}\n")
                
                f.write(f"\nTIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # TimPark payment tool results (always show if tool was enabled)
                if self.config.config.get("timpark_payment", {}).get("use_timpark_payment", False) and timpark_result:
                    if timpark_activated:
                        f.write(f"🎯 REZULTAT TIMPARK PAYMENT TOOL (PRINCIPAL):\n")
                        f.write("=" * 50 + "\n")
                    else:
                        f.write(f"REZULTAT TOOL TIMPARK (PENTRU INFORMARE):\n")
                        f.write("-" * 40 + "\n")
                    
                    f.write(f"Tool activat: {'DA' if timpark_result.get('tool_enabled', False) else 'NU'}\n")
                    f.write(f"Intenție de plată detectată: {'DA' if timpark_result.get('tool_activated', False) else 'NU'}\n")
                    f.write(f"Durată extrasă: {timpark_result.get('duration', 'N/A')}\n")
                    f.write(f"Mesaj: {timpark_result.get('message', 'N/A')}\n")
                    
                    if timpark_result.get('tool_activated', False) and 'automation_result' in timpark_result:
                        automation = timpark_result['automation_result']
                        f.write(f"Automatizare executată: {'DA' if automation.get('success', False) else 'NU'}\n")
                        if automation.get('success', False):
                            f.write(f"Output automatizare: {automation.get('output', '')[:200]}...\n")
                        else:
                            f.write(f"Eroare automatizare: {automation.get('error', 'N/A')}\n")
                    
                    if timpark_activated:
                        f.write("=" * 50 + "\n\n")
                        f.write("🚗 PLATA PARCĂRII A FOST PROCESATĂ CU SUCCES!\n")
                        f.write("⏭️ Nu au fost necesare căutări web suplimentare.\n\n")
                    else:
                        f.write("\n\n")
                
                # Only show other results if TimPark was not activated
                if not timpark_activated:
                    # Final synthesized response (most important)
                    if self.config.config["final_response_generation"]["use_final_response_generation"] and final_synthesized_response:
                        f.write(f"🎯 RĂSPUNS FINAL SINTETIZAT (PRINCIPAL):\n")
                        f.write("=" * 50 + "\n")
                        f.write(final_synthesized_response)
                        f.write("\n\n" + "=" * 50 + "\n\n")
                    
                    # Regular web search results
                    if self.config.config["web_search"]["use_perplexity"] and final_result:
                        f.write(f"REZULTAT CĂUTARE WEB REGULATĂ (PENTRU COMPARAȚIE):\n")
                        f.write("-" * 40 + "\n")
                        f.write(final_result)
                        f.write("\n\n")
                    
                    # Trusted sites search results  
                    if self.config.config["trusted_sites_search"]["use_trusted_sites_search"] and trusted_sites_result:
                        f.write(f"REZULTAT CĂUTARE SITE-URI DE ÎNCREDERE (PENTRU COMPARAȚIE):\n")
                        f.write("-" * 40 + "\n")
                        if trusted_sites_result.get("success"):
                            f.write(f"Domenii selectate ({len(trusted_sites_result.get('selected_domains', []))} total):\n")
                            for i, domain in enumerate(trusted_sites_result.get('selected_domains', []), 1):
                                f.write(f"   {i}. {domain}\n")
                            f.write(f"\nRezultate căutare:\n")
                            f.write(str(trusted_sites_result.get('search_results', 'Nu s-au obținut rezultate')))
                            if trusted_sites_result.get('output_file'):
                                f.write(f"\n\nFișier detaliat salvat: {trusted_sites_result.get('output_file')}")
                        else:
                            f.write(f"Căutarea a eșuat: {trusted_sites_result.get('error', 'Eroare necunoscută')}")
                        f.write("\n\n")
                
                f.write("=" * 60 + "\n")
                f.write("SUMARUL INSTRUMENTELOR FOLOSITE:\n")
                f.write(f"1. Reformulare Query: {'✅ DA' if self.config.config['query_processing']['use_robust_reformulation'] else '❌ NU'}\n")
                f.write(f"2. TimPark Payment Tool: {'✅ DA' if self.config.config.get('timpark_payment', {}).get('use_timpark_payment', False) else '❌ NU'}")
                if timpark_activated:
                    f.write(" 🚗 (EXECUTAT - pașii următori săriți)")
                f.write("\n")
                
                if timpark_activated:
                    f.write(f"3. Căutare Web Regulată: ⏭️ SĂRIT (TimPark executat)\n")
                    f.write(f"4. Căutare Site-uri de Încredere: ⏭️ SĂRIT (TimPark executat)\n")
                    f.write(f"5. Generare Răspuns Final: ⏭️ SĂRIT (TimPark executat)\n")
                else:
                    f.write(f"3. Căutare Web Regulată: {'✅ DA' if self.config.config['web_search']['use_perplexity'] else '❌ NU'}\n")
                    f.write(f"4. Căutare Site-uri de Încredere: {'✅ DA' if self.config.config['trusted_sites_search']['use_trusted_sites_search'] else '❌ NU'}\n")
                    f.write(f"5. Generare Răspuns Final: {'✅ DA' if self.config.config['final_response_generation']['use_final_response_generation'] else '❌ NU'}\n")
                f.write("=" * 60 + "\n")
                
            print(f"✅ Rezultate finale salvate în: {final_filename}")
        
        print(f"\n🎉 PROCESARE COMPLETĂ!")
        if timpark_activated:
            print("🚗 TimPark Payment Tool executat - workflow oprit după pasul 2")
        print("=" * 60)
        
        return {
            "original_question": question,
            "reformulated_query": reformulated_query,
            "timpark_payment_result": timpark_result,
            "regular_web_search_result": final_result,
            "trusted_sites_search_result": trusted_sites_result,
            "final_synthesized_response": final_synthesized_response,
            "config_used": config_name
        }

if __name__ == "__main__":
    print("🤖 AGENT - SISTEM INTEGRAT COMPLET (5 INSTRUMENTE)")
    print("="*60)
    print("📁 Structura organizată în directoare:")
    print("   📂 src/")
    print("   ├── 📂 tools/              # Instrumentele Agent-ului")
    print("   │   ├── robust_user_querries.py    # Reformulare query cu Gemini")
    print("   │   ├── timpark_payment_tool.py    # Automatizare plată parcare TimPark")
    print("   │   ├── perplexity_web_search.py   # Căutare web cu Perplexity")
    print("   │   ├── trusted_sites_search.py    # Căutare site-uri românești de încredere")
    print("   │   └── concatenate_web_searches_into_final_response.py  # Sinteză finală cu Gemini 2.5")
    print("   ├── 📂 instructions/       # Instrucțiunile pentru fiecare tool")
    print("   │   ├── robust_improved_user_querry/  # Prompts pentru Gemini")
    print("   │   ├── platire_timpark/              # Prompts pentru TimPark payment")
    print("   │   ├── web_search/                   # Prompts pentru Perplexity")
    print("   │   ├── trusted_sites/                # Prompts pentru site-uri de încredere")
    print("   │   └── concatenate_responses_get_final_response/  # Prompts pentru sinteza finală")
    print("   ├── 📂 results/            # Rezultatele procesării")
    print("   │   └── agent_results/               # Output-ul Agent-ului")
    print("   ├── 📄 agent_config.json   # Configurația principală")
    print("   └── 📄 agent.py            # Agentul principal")
    print()
    
    # Test with the single config file
    print("🧪 Testing Agent cu toate instrumentele integrate...")
    print("WORKFLOW INTELIGENT (CONDIȚIONAT):")
    print("   1️⃣  Reformulare query cu Gemini (opțional)")
    print("   2️⃣  💳 Analiză intenție plată parcare TimPark (opțional)")
    print("   📋  ↳ DACĂ TimPark se execută → STOP (pașii 3-5 sunt săriți)")
    print("   3️⃣  Căutare web regulată cu Perplexity (doar dacă TimPark NU s-a executat)")
    print("   4️⃣  Căutare pe site-uri românești de încredere (doar dacă TimPark NU s-a executat)")
    print("   5️⃣  🆕 Sinteză finală cu Gemini 2.5 Flash (doar dacă TimPark NU s-a executat)")
    print("   6️⃣  Salvare rezultate adaptive și finale")
    print()
    
    agent = Agent("agent_config.json")
    result = agent.process_query()
    
    print("\n" + "="*80)
    print("✅ Test completed! Verificați fișierele în results/agent_results/")
    print("\n📖 Cum să folosiți:")
    print("1. Modificați agent_config.json pentru a controla comportamentul")
    print("2. Rulați: agent = Agent('agent_config.json')")
    print("3. Apoi: agent.process_query('întrebarea dumneavoastră', 'nume_config')")
    print("4. Toate setările sunt controlate din agent_config.json")
    print("\n🔧 Parametri controlabili din config:")
    print("   • use_robust_reformulation: activează/dezactivează reformularea Gemini")
    print("   • use_timpark_payment: activează/dezactivează tool-ul de plată parcare TimPark")
    print("   • use_perplexity: activează/dezactivează căutarea web regulată")
    print("   • use_trusted_sites_search: activează/dezactivează căutarea pe site-uri de încredere")
    print("   • use_final_response_generation: activează/dezactivează sinteza finală")
    print("   • use_rag_context: activează/dezactivează integrarea contextului RAG local")
    print("   • rag_domains: domeniile pentru care să se caute context RAG (ex: ['dfmt.ro', 'timpark.ro'])")
    print("   • rag_context_path: calea către fișierele de context RAG (default: 'rag_context')")
    print("   • gemini_temperature: controlează creativitatea (0.1-1.0)")
    print("   • city_hint: orașul pentru căutare (ex: 'timisoara', 'bucuresti')")
    print("   • output_folder: directorul pentru rezultate")
    print("\n💳 Nou! Tool de Plată Parcare TimPark (cu logică inteligentă):")
    print("   • Analizează automat intenția utilizatorului de plată parcare")
    print("   • Detectează Timișoara ca locație implicită")
    print("   • Extrage durata parcării (30min-12h)")
    print("   • Execută automatizarea plății dacă intenția este clară")
    print("   • 🚗 IMPORTANT: Când se execută, OPREȘTE workflow-ul (nu mai face căutări web)")
    print("   • Exemple: 'plateste parcarea 2 ore', 'achita parcarea centru'")
    print("\n🏛️ Căutare pe site-uri românești de încredere (doar dacă TimPark NU se execută):")
    print("   • Selecție inteligentă de domenii guvernamentale cu Gemini 2.5 Flash")
    print("   • Căutare filtrată doar pe site-urile selectate cu Perplexity")
    print("   • Rezultate oficiale cu citări corecte")
    print("\n🎯 Nou! Sinteză finală cu Gemini 2.5 Flash (doar dacă TimPark NU se execută):")
    print("   • Combină rezultatele din toate instrumentele anterioare")
    print("   • Evită redundanța și prioritizează sursele oficiale")
    print("   • Formatează ca instrucțiuni pas cu pas, ușor de urmărit")
    print("   • Răspuns final coerent și cuprinzător pentru utilizator")
    print("\n📋 Structura instrucțiunilor:")
    print("   • robust_improved_user_querry/: Prompts pentru reformularea query-urilor")
    print("   • platire_timpark/: Prompts pentru analiza intenției de plată parcare")
    print("   • web_search/: Prompts pentru optimizarea căutării web")
    print("   • trusted_sites/: Prompts pentru site-urile de încredere")
    print("   • concatenate_responses_get_final_response/: Prompts pentru sinteza finală")
    print("   • idea/: Documentația conceptuală și ghiduri de utilizare")
    print("\n🔄 Logica Workflow-ului Nou:")
    print("   📊 SCENARIU A: TimPark Payment NU se activează")
    print("      → Execută toate cele 5 instrumente (workflow complet)")
    print("   📊 SCENARIU B: TimPark Payment se activează și execută plata")
    print("      → Oprește după pasul 2, săre peste pașii 3-5 (nu mai sunt necesare căutări)")
    print("   📊 Avantaj: Eficiență maximă - nu pierdem timp cu căutări inutile după ce plata e făcută")
