from playwright.async_api import async_playwright
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from dotenv import load_dotenv
import os
import requests
from langchain.agents import Tool
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_experimental.tools import PythonREPLTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
import resend
from tavily import TavilyClient
import asyncio


load_dotenv(override=True)


NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")
resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(message: str):
    """
    Send out an push notification with the given subject and HTML body to all sales prospects.
    """
    try:
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",  
            "to": NOTIFICATION_EMAIL,         
            "subject": "Test",
            "html": message
        })

        print("Resend response:", response)
        return {"status": "success"}

    except Exception as e:
        print("Resend error:", e)
        return {
            "status": "error",
            "message": str(e)
        }
    


def websearch(query:str):
    """ Search the web for the given query """
    tavili_api_key=os.getenv("TAVILY_API")
    tavily_client = TavilyClient(tavili_api_key)
    response = tavily_client.search(query)
    
    return str(response)
    
async def playwright_tools():
    playwright=await async_playwright().start()
    browser=await playwright.chromium.launch(headless=False)
    toolkit=PlayWrightBrowserToolkit.from_browser(async_browser=browser)
    return toolkit.get_tools(),browser,playwright

async def playwright_tool(url:str):
    tools,browswer,playwright= await playwright_tools()

    tool_dict = {tool.name:tool for tool in tools}

    navigate_tool = tool_dict.get("navigate_browser")
    extract_text_tool = tool_dict.get("extract_text")

        
    await navigate_tool.arun({"url": url})
    text = await extract_text_tool.arun({})
    return str(text)

def get_file_tools():
    toolkit=FileManagementToolkit(root_dir="sandbox")
    return toolkit.get_tools()

async def other_tools():
    push_tool=Tool(name="send_push_notification", 
                   func=send_email,
                   description="use this when you want to send push notification. Send notification in beautiful HTML body from markdown")
    file_tools=get_file_tools()

    tool_search=Tool(
        name="search",
        func=websearch,
        description="use this tool when you want get results of an online web search"
    )

    browse_tool = Tool(
    name="browse_webpage",
    func=lambda url: playwright_tool,
    description="Open a webpage and extract its text content"
    )

    wikipedia = WikipediaAPIWrapper()
    wiki_tool = WikipediaQueryRun(api_wrapper=wikipedia)

    python_repl=PythonREPLTool()

    return file_tools+[push_tool,tool_search,python_repl,wiki_tool,browse_tool]
