import os
from openai import AzureOpenAI
import base64
import json
import time
import errno

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2023-12-01-preview"
)


def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                # Not a "file in use" error, re-raise
                raise
            # File is being written to, wait a bit and retry
            time.sleep(0.1)



def generate_new_line(base64_image):
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        },
    ]


def analyze_image(base64_image, script):
    response = client.chat.completions.create(
        # model="gpt-4-vision-preview",
        model= "gpt-4v",
        messages=[
            {
                "role": "system",
                "content": """
                You are a fiction writer. Narrate the picture.
                Make it snarky and funny. Don't repeat yourself. Connect the pictures into a story. If I do anything remotely interesting, make a big deal about it!
                """,
            },
        ]
        + script
        + generate_new_line(base64_image),
        max_tokens=500,
    )
    response_text = response.choices[0].message.content
    return response_text


def main():
    script = []
    i=1

    while True and i < 7:
        # path to your image
        # image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")
        image_path = os.path.join(os.getcwd(), f"static/images/story{i}.png")
        i+=1

        # getting the base64 encoding
        b64_image = encode_image(image_path)

        # analyze posture
        print("Generating Story...")
        analysis = analyze_image(b64_image, script=script)

        print("You're Story is:")
        print(analysis)

        play_audio(analysis)

        script = script + [{"role": "assistant", "content": analysis}]

        # wait for 5 seconds
        time.sleep(5)


if __name__ == "__main__":
    main()
