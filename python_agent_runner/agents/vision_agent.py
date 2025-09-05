import openai
import os
import base64
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class VisionAgent:
    def __init__(self):
        self.vision_model = "gpt-4o"
        print(f"Vision Agent initialized with model: {self.vision_model}")

    def _encode_image(self, image_path):
        """Encodes an image file into a base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def create_blueprint_from_image(self, user_prompt, image_path):
        """
        Analyzes a UI mockup image and generates a detailed blueprint for code generation.
        """
        print(f"Vision Agent: Analyzing image at {image_path}...")
        base64_image = self._encode_image(image_path)

        try:
            response = openai.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert UI/UX designer and frontend developer. Your task is to analyze an image of a webpage mockup and a user prompt. Create a detailed, step-by-step 'blueprint' of instructions for another AI agent to write the HTML and CSS code. Describe the layout, colors, fonts, and all UI elements precisely."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1024
            )
            blueprint = response.choices[0].message.content
            print("Vision Agent: Blueprint generated successfully.")
            return blueprint
        except Exception as e:
            print(f"Vision Agent Error: {e}")
            return f"Error analyzing image: {e}"
