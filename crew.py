from crewai import Agent, Task, Crew, Process
from tools.yf_tech_analysis_tool import yf_tech_analysis
from tools.yf_fundamental_analysis_tool import yf_fundamental_analysis
from tools.sentiment_analysis_tool import sentiment_analysis
from tools.competitor_analysis_tool import competitor_analysis
from tools.risk_assessment_tool import risk_assessment
from litellm import completion  
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI
import os 

os.environ["GOOGLE_API_KEY"] = "AIzaSyCROWEOFoXucS-USWu_nG3184_IbHZJo3g"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY")) 

class GeminiLLM:
    def __init__(self):
        self.model = "gemini/gemini-2.0-flash"  # LiteLLM format: provider/model
        os.environ['GEMINI_API_KEY'] = "AIzaSyCROWEOFoXucS-USWu_nG3184_IbHZJo3g" # Replace with your key

    def __call__(self, prompt: str) -> str:
        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            print(f"Gemini LLM error: {str(e)}")
            return "LLM unavailable"
        
# class OllamaStreamingLLM:
#     def __init__(self):
#         self.model = "ollama/llama3"  # Must include "ollama/" prefix
#         self.api_base = "http://localhost:11434"
        
#     def __call__(self, prompt: str) -> str:
#         try:
#             full_response = ""
#             response = completion(
#                 model=self.model,
#                 messages=[{"content": prompt, "role": "user"}],
#                 api_base=self.api_base,
#                 stream=True
#             )
            
#             for chunk in response:
#                 if 'content' in chunk.choices[0].delta:
#                     full_response += chunk.choices[0].delta.content
            
#             return full_response
            
#         except Exception as e:
#             print(f"Ollama error: {str(e)}")
#             return "LLM unavailable" 
    
def create_crew(stock_symbol):
    # Initialize Ollama LLM
    # llm = OllamaStreamingLLM()  # Make sure you have the llama2 model installed in Ollama
    llm = GeminiLLM()

    # Define Agents
    researcher = Agent(
        role='Stock Market Researcher',
        goal='Gather and analyze comprehensive data about the stock',
        backstory="You're an experienced stock market researcher with a keen eye for detail and a talent for uncovering hidden trends.",
        tools=[yf_tech_analysis, yf_fundamental_analysis, competitor_analysis],
        llm=llm
    )

    analyst = Agent(
        role='Financial Analyst',
        goal='Analyze the gathered data and provide investment insights',
        backstory="You're a seasoned financial analyst known for your accurate predictions and ability to synthesize complex information.",
        tools=[yf_tech_analysis, yf_fundamental_analysis, risk_assessment],
        llm=llm
    )

    sentiment_analyst = Agent(
        role='Sentiment Analyst',
        goal='Analyze market sentiment and its potential impact on the stock',
        backstory="You're an expert in behavioral finance and sentiment analysis, capable of gauging market emotions and their effects on stock performance.",
        tools=[sentiment_analysis],
        llm=llm
    )

    strategist = Agent(
        role='Investment Strategist',
        goal='Develop a comprehensive investment strategy based on all available data',
        backstory="You're a renowned investment strategist known for creating tailored investment plans that balance risk and reward.",
        tools=[],
        llm=llm
    )

    # Define Tasks
    research_task = Task(
        description=f"""Conduct thorough research on {stock_symbol} including:
        1. Technical analysis (trends, indicators, patterns)
        2. Fundamental analysis (financial ratios, valuation metrics)
        3. Competition of the stock provided to you in detail
        Provide a detailed report with all the findings.""",
        agent=researcher,
        expected_output="A comprehensive research report with financial metrics, and competitor comparison."
    )

    sentiment_task = Task(
        description=f"""Analyze market sentiment for {stock_symbol} by:
        1. Evaluating news sentiment
        2. Analyzing news sentiments and diggind up if some crucial breakthorugh happened related to the company
        3. Identifying potential sentiment-driven price movements""",
        agent=sentiment_analyst,
        expected_output="Sentiment analysis report with quantified sentiment scores and potential impact assessment."
    )

    analysis_task = Task(
        description=f"""Synthesize all research data on {stock_symbol} to:
        1. Evaluate risk-reward profile
        2. Identify key strengths and weaknesses
        3. Assess valuation attractiveness
        4. Highlight potential catalysts""",
        agent=analyst,
        expected_output="Detailed investment analysis with risk assessment and opportunity evaluation."
    )

    strategy_task = Task(
        description=f"""Develop investment strategy for {stock_symbol} considering:
        1. Different time horizons (short, medium, long-term)
        2. Various risk profiles (conservative, moderate, aggressive)
        3. Current market conditions
        4. All previous analysis findings""",
        agent=strategist,
        expected_output="Comprehensive investment strategy with clear recommendations for different investor types."
    )

    # Create Crew
    crew = Crew(
        agents=[researcher, sentiment_analyst, analyst, strategist],
        tasks=[research_task, sentiment_task, analysis_task, strategy_task],
        verbose=True,
        process=Process.sequential
    )

    return crew

def run_analysis(stock_symbol):
    # Initialize Ollama LLM
    llm = GeminiLLM()
    
    # Initialize a dictionary to store individual agent outputs
    agent_outputs = {}
    
    # 1. Researcher Task
    print(f"\n======= Executing Task 1: Stock Market Researcher =======")
    researcher = Agent(
        role='Stock Market Researcher',
        goal='Gather and analyze comprehensive data about the stock',
        backstory="You're an experienced stock market researcher with a keen eye for detail and a talent for uncovering hidden trends.",
        tools=[yf_tech_analysis, yf_fundamental_analysis, competitor_analysis],
        llm=llm
    )
    
    research_task = Task(
        description=f"""Conduct thorough research on {stock_symbol} including:
        1. Technical analysis (trends, indicators, patterns)
        2. Fundamental analysis (financial ratios, valuation metrics)
        3. Competitive landscape analysis
        Provide a detailed report with key findings.""",
        agent=researcher,
        expected_output="A comprehensive research report with financial metrics, and competitor comparison."
    )
    
    research_crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        process=Process.sequential
    )
    
    research_result = research_crew.kickoff()
    print(research_result)
    agent_outputs['Stock Market Researcher'] = research_result
    print("Task 1 completed by Stock Market Researcher")
    
    # 2. Sentiment Analyst Task
    print(f"\n======= Executing Task 2: Sentiment Analyst =======")
    sentiment_analyst = Agent(
        role='Sentiment Analyst',
        goal='Analyze market sentiment and its potential impact on the stock',
        backstory="You're an expert in behavioral finance and sentiment analysis, capable of gauging market emotions and their effects on stock performance.",
        tools=[sentiment_analysis],
        llm=llm
    )
    
    sentiment_task = Task(
        description=f"""Analyze market sentiment for {stock_symbol} by:
        1. Evaluating news sentiment
        2. Analyzing news sentiments and digging up if some crucial breakthrough happened related to the company
        3. Identifying potential sentiment-driven price movements""",
        agent=sentiment_analyst,
        expected_output="Sentiment analysis report with quantified sentiment scores and potential impact assessment."
    )
    
    sentiment_crew = Crew(
        agents=[sentiment_analyst],
        tasks=[sentiment_task],
        process=Process.sequential
    )
    
    sentiment_result = sentiment_crew.kickoff()
    print(sentiment_result)
    agent_outputs['Sentiment Analyst'] = sentiment_result
    print("Task 2 completed by Sentiment Analyst")
    
    # 3. Financial Analyst Task
    print(f"\n======= Executing Task 3: Financial Analyst =======")
    analyst = Agent(
        role='Financial Analyst',
        goal='Analyze the gathered data and provide investment insights',
        backstory="You're a seasoned financial analyst known for your accurate predictions and ability to synthesize complex information.",
        tools=[yf_tech_analysis, yf_fundamental_analysis, risk_assessment],
        llm=llm
    )
    
    analysis_task = Task(
        description=f"""Synthesize all research data on {stock_symbol} to:
        1. Evaluate risk-reward profile
        2. Identify key strengths and weaknesses
        3. Assess valuation attractiveness
        4. Highlight potential catalysts
        
        Use the following research data as context:
        {research_result}
        {sentiment_result}""",
        agent=analyst,
        expected_output="Detailed investment analysis with risk assessment and opportunity evaluation."
    )
    
    analysis_crew = Crew(
        agents=[analyst],
        tasks=[analysis_task],
        process=Process.sequential
    )
    
    analysis_result = analysis_crew.kickoff()
    print(analysis_result)
    agent_outputs['Financial Analyst'] = analysis_result
    print("Task 3 completed by Financial Analyst")
    
    # 4. Investment Strategist Task
    print(f"\n======= Executing Task 4: Investment Strategist =======")
    strategist = Agent(
        role='Investment Strategist',
        goal='Develop a comprehensive investment strategy based on all available data',
        backstory="You're a renowned investment strategist known for creating tailored investment plans that balance risk and reward.",
        tools=[],
        llm=llm
    )
    
    strategy_task = Task(
        description=f"""Develop investment strategy for {stock_symbol} considering:
        1. Different time horizons (short, medium, long-term)
        2. Various risk profiles (conservative, moderate, aggressive)
        3. Current market conditions
        4. All previous analysis findings
        
        Use the following analysis data as context:
        {research_result}
        {sentiment_result}
        {analysis_result}""",
        agent=strategist,
        expected_output="Comprehensive investment strategy with clear recommendations for different investor types."
    )
    
    strategy_crew = Crew(
        agents=[strategist],
        tasks=[strategy_task],
        process=Process.sequential
    )
    
    strategy_result = strategy_crew.kickoff()
    print(strategy_result)
    agent_outputs['Investment Strategist'] = strategy_result
    print("Task 4 completed by Investment Strategist")
    
    # # Full sequential analysis
    # print("\n======= Running Full Analysis =======")
    # crew = create_crew(stock_symbol)
    # final_result = crew.kickoff()
    
    return {
        "individual_analyses": agent_outputs
    }
