import base64
import boto3
import json
import os


def generateTextToImage(prompt: str, model_id: str, negative_prompt: str, seed: int, aspect_ratio: str, output_format: str):

    bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")

    body = {
        "prompt": prompt,
        "mode": "text-to-image",
        "negative_prompt": negative_prompt,
        "seed": seed,
        "aspect_ratio": aspect_ratio,
        "output_format": output_format
    }
    response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
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

    return image_path
    
    

def ImageToImage(prompt: str, model_id: str, negative_prompt: str, seed: int, aspect_ratio: str, output_format: str, image: str, strength: float):

    bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")

    body = {
        "prompt": prompt,
        "mode": "image-to-image",
        "negative_prompt": negative_prompt,
        "seed": seed,
        "aspect_ratio": aspect_ratio,
        "output_format": output_format,
        "image": image,
        "strength": strength
    }

    response = bedrock.invoke_model(modelId=model_id, body=json.dumps(body))

    model_response = json.loads(response["body"].read())

    base64_image_data = model_response["images"][0]

    i, output_dir = 1, "variations_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    while os.path.exists(os.path.join(output_dir, f"img_{i}.png")):
        i += 1

    image_data = base64.b64decode(base64_image_data)

    image_path = os.path.join(output_dir, f"img_{i}.png")
    with open(image_path, "wb") as file:
        file.write(image_data)

    return image_path
