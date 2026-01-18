import base64
import boto3
import json
import os

MODEL_ID = "stability.sd3-5-large-v1:0" 

bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")

print("Enter a prompt for the text-to-image model:")
prompt = input()

body = {
    "prompt": prompt,
    "mode": "text-to-image"
}
response = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(body))

model_response = json.loads(response["body"].read())

base64_image_data = model_response["images"][0]

i, output_dir = 1, "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
while os.path.exists(os.path.join(output_dir, f"img_{i}.png")):
    i += 1

image_data = base64.b64decode(base64_image_data)

image_path = os.path.join(output_dir, f"img_{i}.png")
with open(image_path, "wb") as file:
    file.write(image_data)

print(f"The generated image has been saved to {image_path}")
