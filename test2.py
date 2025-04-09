from typing import List
from langchain.tools import StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from datetime import datetime
from pathlib import Path

# Step 1: Define the input schema
class CROAnalysisInput(BaseModel):
    image_urls: List[str] = Field(
        ...,
        description="List of image URLs for Nike product pages (PLPs or PDPs)"
    )

# Step 2: Define the tool function
def run_cro_analysis(image_urls: List[str]) -> str:
    # Initialize the model
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1, max_tokens=4096, verbose=True, top_p=0.9)
        
    # Build content prompt
    content_prompt = {
        "type": "text",
        "text": (
            "You are a Senior UX Specialist in E-Commerce Conversion Rate Optimization (CRO)."
            "\n\nAnalyze the **visible content** of the following Nike product pages — these can be either Product Listing Pages (PLPs) or Product Detail Pages (PDPs)."
            "\n\nFor each screenshot:"
            "\n- Include a title like '**Page 1: Product Listing Page**' or '**Page 2: Product Detail Page**'."
            "\n- Then break down your analysis under three clear categories:"
            "\n\n### Content"
            "- What's missing that could build trust, reduce friction, or improve clarity?"
            "- What’s irrelevant, redundant, or distracting to the user?"
            "- Are the products shown **suitable and appealing** in this context? Would more relevant or high-impact items improve user engagement?"
            "- Does the featured product mix align with what users likely expect or need on this page?"
            "- Could repositioning or prioritizing specific products **enhance visual appeal or conversion intent**?"
            "\n\n### Layout"
            "- Are key actions like CTAs positioned for fast decisions?"
            "- Identify layout issues (e.g., padding, spacing, alignment)."
            "- Suggest small layout wins to improve visual hierarchy and clarity."
            "\n\n### Design"
            "- Evaluate typography, button visibility, whitespace, color usage, and imagery."
            "- Be **visually specific**: e.g., 'Increase font size of price by ~20%', 'Add background contrast to size selector', etc."
            "\n\nEach bullet should be short, direct, and **actionable**. Avoid generic UX advice."
            "\n\nMark high-impact conversion suggestions with a 🔺 symbol and explain briefly and shortly with no more than 3 words — why it will help (e.g., 'reduces hesitation', 'improves scannability')."
        )
    }


    # Add image prompts
    image_prompts = [
        {
            "type": "image_url",
            "image_url": {
                "url": url,
                "detail": "high"
            }
        }
        for url in image_urls
    ]

    # Send to LLM
    message = HumanMessage(content=[content_prompt] + image_prompts)
    response = llm([message])

    # Save to Markdown
    markdown_output = response.content
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"nike_cro_analysis_{timestamp}.md"
    Path(filename).write_text(markdown_output, encoding="utf-8")

    return f"Analysis complete. Saved Markdown to: {filename}"

# Step 3: Create the LangChain StructuredTool
cro_analysis_tool = StructuredTool.from_function(
    func=run_cro_analysis,
    name="nike_cro_analysis",
    description="Analyze Nike product page screenshots (PLP or PDP) for UX and CRO improvements.",
    args_schema=CROAnalysisInput
)

# Example usage
result = cro_analysis_tool.invoke({
    "image_urls": []
})
print(result)