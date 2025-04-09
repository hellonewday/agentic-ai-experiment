from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc-8f5e9e2ff45844dcba5078cd05486a0b")

content = app.scrape_url("https://www.nike.com/sg/launch",
{
     "formats": ['screenshot'],
      "actions": [
        {
            "type": "wait",
            "milliseconds": 1000,
        },
        {
            "type": "screenshot",
            "fullPage": True
        }
    ],
     
})

print(content['screenshot'])