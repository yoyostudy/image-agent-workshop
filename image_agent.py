import openai
import json
from dotenv import load_dotenv
from details.generate_tools_schema import generate_json_schema
from tools import *

load_dotenv()

class image_agent:
    def __init__(self):
        self.client = openai.OpenAI()

        self.tools = []
        self.tools.append(generate_json_schema(self.create_image_mask_file_by_description))


    def create_image_mask_file_by_description(self, image_path, description):
        detected_object = detect_object(image_path, description)
        if detected_object:
            return extract_object_mask(image_path, detected_object)
        return None

    def run(self, query: str):
        assistant = self.client.beta.assistants.create(
            model='gpt-4o-2024-08-06',
            instructions="""
            You are an image edit assistant. Your job is helping the user edit images using the tools provided. 
            """,
            tools=self.tools,
            name="image-agent",
        )

        thread = self.client.beta.threads.create()
        self.client.beta.threads.messages.create(thread_id=thread.id, role="user", content=query)
        run = self.client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant.id,)

        max_turns = 50
        for _ in range(max_turns):
            messages = self.client.beta.threads.messages.list(
                        thread_id=thread.id,
                        run_id=run.id,
                        order="desc",
                        limit=1,
                    )
            
            if run.status == "completed":
                return  next((
                        content.text.value
                        for content in messages.data[0].content
                        if content.type == "text"
                    ),
                    None,
                )

            elif run.status == "requires_action":
                func_tool_outputs = []
                for tool in run.required_action.submit_tool_outputs.tool_calls:
                    print(f"Calling Function: {tool.function.name}")
                    print(tool.function.arguments)
                    if tool.function.name == "create_image_mask_file_by_description":
                        func_output = self.create_image_mask_file_by_description(**json.loads(tool.function.arguments))
                        func_tool_outputs.append({"tool_call_id": tool.id, "output": func_output})
                    else:
                        raise Exception("Function not available")

                # Submit the function call outputs back to OpenAI
                run = self.client.beta.threads.runs.submit_tool_outputs_and_poll(thread_id=thread.id, run_id=run.id, tool_outputs=func_tool_outputs)

            elif run.status == "failed":
                    print(f"Agent run failed for the reason: {run.last_error}")
                    break
            else:
                print(f"Run status {run.status} not yet handled")
        else:
            print("Reached maximum reasoning turns, maybe increase the limit?")

if __name__ == "__main__":
    agent = image_agent()
    query = query = "Based on the 'original_image.png', replace the horse with a dairy cow standing on the grass."
    result =agent.run(query)
    print(f"Response from LLM: {result}")