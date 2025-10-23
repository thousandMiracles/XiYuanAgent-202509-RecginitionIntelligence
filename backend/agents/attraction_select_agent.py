from agno.agent import Agent, RunOutput, RunOutputEvent, RunEvent
from agno.models.deepseek import DeepSeek

from tools.attraction_select import AmapTools

agent = Agent(
    model=DeepSeek(id="deepseek-chat"),
    tools=[AmapTools(key="1f13f85e98b8e75644d9681cb2bcc64b")],
    instructions="XXX",
    markdown=True
)

response: RunOutput = agent.run("Trending startups and products.")
# Print the response
print(response.content)
