import asyncio
from playwright.async_api import async_playwright
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit


async def playwright_tools():
    playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(
        headless=False
    )

    toolkit = PlayWrightBrowserToolkit.from_browser(
        async_browser=browser
    )

    return toolkit.get_tools(), browser, playwright


async def main():
    tools, browser, playwright = await playwright_tools()

    print("\nAvailable tools:")
    for tool in tools:
        print("-", tool.name)

    # Create lookup dictionary
    tool_map = {tool.name: tool for tool in tools}

    # Print exact tool names
    print("\nTool names:")
    print(tool_map.keys())

    # Usually these names exist:
    navigate_tool = tool_map["navigate_browser"]
    extract_tool = tool_map["extract_text"]

    print("\nNavigating...")
    nav_result = await navigate_tool.ainvoke(
        {"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"}
    )

    print("Navigation Result:")
    print(nav_result)

    print("\nExtracting text...")
    text_result = await extract_tool.ainvoke({})

    print("\nExtracted Text:")
    print(text_result[:2000])  # first 2000 chars

    input("\nPress Enter to close browser...")

    await browser.close()
    await playwright.stop()


asyncio.run(main())