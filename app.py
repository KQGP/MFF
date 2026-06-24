import streamlit as st
from google import genai
from google.genai import types
from exa_py import Exa
from firecrawl import FirecrawlApp
import json
import time

# --- 1. USER INTERFACE CONFIGURATION ---
st.set_page_config(page_title="AI Fashion Finder", page_icon="🛍️", layout="wide")
st.title("🛍️ AI Multimodal Fashion Finder (with YR Market Conversion)")
st.subheader("Upload clothing items to find matches online with real-time currency adjustments for Yemen.")

# --- 2. SECURE HARDCODED API KEYS ---
gemini_key = st.sidebar.text_input(
    "Gemini API Key", 
    value="AQ.Ab8RN6IaccDitd0Bzb9udvErtEHXfZhs7kZjJbJ8Q5fNRl4eCQ", 
    type="password"
)
exa_key = st.sidebar.text_input(
    "Exa API Key", 
    value="f1854d92-e342-4e50-90a6-f410e5addcea", 
    type="password"
)
firecrawl_key = st.sidebar.text_input(
    "Firecrawl API Key", 
    value="fc-f7f9b17cb02543c1a35e436108832f96", 
    type="password"
)

# --- 3. MULTI-PRODUCT UPLOAD INTERFACE ---
st.header("📸 Step 1: Upload Your Products")
uploaded_files = st.file_uploader(
    "Drag and drop one or multiple clothing photos here", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

product_inputs = {}

if uploaded_files:
    st.write(f"### 📝 Step 2: Add Details for Your {len(uploaded_files)} Items")
    cols = st.columns(len(uploaded_files))
    
    for idx, file in enumerate(uploaded_files):
        with cols[idx]:
            st.image(file, caption=f"Product {idx+1}", use_container_width=True)
            materials = st.text_input(f"Materials/Quality (Product {idx+1})", placeholder="e.g., 100% Silk", key=f"mat_{idx}")
            tags = st.text_input(f"Extra Tags (Product {idx+1})", placeholder="e.g., Summer Dress", key=f"tag_{idx}")
            
            product_inputs[idx] = {
                "file": file,
                "materials": materials,
                "tags": tags
            }

    st.markdown("---")
    st.header("🚀 Step 3: Run Match Engine")
    
    if st.button("🔍 Search All Products Online", type="primary"):
        if not gemini_key or not exa_key or not firecrawl_key:
            st.error("Please provide all 3 API keys in the sidebar to start!")
        else:
            gemini_client = genai.Client(
                api_key=gemini_key,
                http_options=types.HttpOptions(
                    retry_options=types.HttpRetryOptions(
                        attempts=3,
                        initial_delay=2.0,
                        http_status_codes=[503]
                    )
                )
            )
            exa = Exa(api_key=exa_key)
            firecrawl = FirecrawlApp(api_key=firecrawl_key)
            
            for idx, data in product_inputs.items():
                st.write(f"## 📊 Results for Product {idx+1}")
                
                with st.spinner(f"Analyzing Product {idx+1}..."):
                    try:
                        image_bytes = data["file"].getvalue()
                        
                        # A. Generate search query using corrected types.Part wrapper
                        vision_prompt = f"""
                        Analyze this clothing item. Give me a highly descriptive search engine text query. 
                        Incorporate these details if provided: Material: {data['materials']}, Tags: {data['tags']}.
                        """
                        
                        image_part = types.Part.from_bytes(
                            data=image_bytes,
                            mime_type=data["file"].type
                        )
                        
                        vision_res = gemini_client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[image_part, vision_prompt]
                        )
                        search_query = vision_res.text
                        
                        # B. Web Search (Updated parameter format)
                        target_domains = ["shein.com", "namshi.com", "boutiqaat.com", "styli.com", "ounass.com"]
                        search_results = exa.search(
                            search_query,
                            num_results=4,
                            include_domains=target_domains,
                            type="auto"
                        )
                        
                        # C. Scrape web data
                        scraped_pages = []
                        for result in search_results.results:
                            try:
                                page_data = firecrawl.scrape_url(result.url, params={'formats': ['markdown']})
                                scraped_pages.append({
                                    "url": result.url,
                                    "markdown": page_data.get('markdown', '')[:2500]
                                })
                            except Exception:
                                scraped_pages.append({"url": result.url, "markdown": result.text if hasattr(result, 'text') else "No data"})
                        
                        # D. Multi-Factor Grading Layer
                        grading_prompt = f"""
                        You are an expert fashion supply-chain auditor. Compare the user's original item to these {len(scraped_pages)} web pages.
                        Original item attributes: Material: '{data['materials']}', Context tags: '{data['tags']}'.
                        
                        Carefully parse the price found on each web page. 
                        Convert whatever currency you find (SAR, AED, etc.) into USD.
                        
                        Return your response ONLY as a valid, raw JSON array matching this exact schema:
                        [
                          {{
                            "url": "Product page link",
                            "page_currency_price": "The exact original price and currency from the page (e.g., '150 SAR' or '45 AED')",
                            "price_usd": 39.99,
                            "category": "Choose one: ['Identical', 'Very Similar', 'Low-Quality Replica']",
                            "match_score": "e.g., 85%",
                            "reasoning": "Brief sentence explaining quality/match"
                          }}
                        ]

                        Scraped Web Pages Data:
                        {json.dumps(scraped_pages)}
                        """
                        
                        grading_res = gemini_client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=grading_prompt
                        )
                        
                        clean_json = grading_res.text.strip().replace("```json", "").replace("```", "")
                        results_list = json.loads(clean_json)
                        
                        # --- 5. RENDER CLEAN METRICS WITH PYTHON CONVERSION ---
                        for item in results_list:
                            with st.container(border=True):
                                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                                
                                try:
                                    usd_val = float(item['price_usd'])
                                    yr_market_price = usd_val * 530
                                    yr_display = f"{yr_market_price:,.0f} YR"
                                    usd_display = f"${usd_val:,.2f}"
                                except Exception:
                                    yr_display = "Calculation Error"
                                    usd_display = "N/A"

                                with c1:
                                    st.markdown(f"**🔗 Link:** [{item['url']}]({item['url']})")
                                    st.caption(f"💬 *Reasoning:* {item['reasoning']}")
                                with c2:
                                    st.metric("Categorization", item['category'])
                                with c3:
                                    st.metric("Page Currency", item['page_currency_price'])
                                with c4:
                                    st.metric("Market Price (YR)", yr_display, delta=f"Based on {usd_display}")
                                    
                        time.sleep(4) # Rate limit throttle safety
                        
                    except Exception as e:
                        st.error(f"Failed processing Product {idx+1}. Error Details: {str(e)}")
else:
    st.info("💡 Ready! Please upload one or more photos above to begin tracking regional prices.")