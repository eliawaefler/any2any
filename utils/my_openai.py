"""
here are all functions that directly call openai.
"""

import os
from openai import OpenAI
import requests
import base64

client = OpenAI()
system_prompts = {
    "doc_generator": "Du bist eine Maschine, die synthetische Dokumente generiert, "
                     "für spätere Klassifizierungsaufgaben. Du antwortest im JSON format.",
    "assistent": "Du bist ein hilfreicher Assistent.",
    "doc_classifier": "Du bist eine Maschine, die Dokumente klassifiziert. "
                      "Du antwortest IMMER in einer Python-Liste. verwende innerhalb der liste nur python typen."
                      "beginne die antwort mit [ und beende sie mit ]",
    "python": "du bist teil eines python scripts und führst haargenau die instruktionen des prompts aus. du antwortest"
              "in ausschliesslich in python typen wie str, int, float list, dict usw. stelle sicher, "
              "dass deine ganze antwort verwendet werden kann. antworte kurz und präzise, keine weiteren bemerkungen. "
              "eg1: user prompt: was gibt 3+3? antwort: 6"
              "eg2: user prompt: was das gegenteil von dunkel? antwort: 'hell'"
              "eg3: user prompt: nenne drei tiere. antwort: ['Tiger', 'Affe', 'Kuh']"
}


def image_bytes_to_base64(image_bytes):
    """
    Converts an image from bytes to a Base64 encoded string.

    Args:
    image_bytes (bytes): Byte content of the image.

    Returns:
    str: A Base64 encoded string of the image.
    """
    return base64.b64encode(image_bytes).decode('utf-8')


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return str(base64.b64encode(image_file.read()).decode('utf-8'))


def gpt4_new(prompt_text, system_p="assistent", temp=0, gpt_model="gpt-4"):
    try:
        system_prompt = system_prompts[system_p]
    except KeyError:
        system_prompt = str(system_p)

    gpt_response = client.chat.completions.create(
        model=gpt_model,
        temperature=temp,
        messages=[{"role": "system",
                   "content": system_prompt},
                  {"role": "user", "content": prompt_text}])
    return gpt_response.choices[0].message.content


def vectorize_data(data_input):
    # input can be list or string:

    if isinstance(data_input, list):
        # returning a dictionary
        my_dict = {}
        for item in data_input:
            my_dict[str(item)] = client.embeddings.create(input=data_input,
                                                          model="text-embedding-ada-002").data[0].embedding
        return my_dict

    elif isinstance(data_input, str):
        # returning just the vector
        return client.embeddings.create(input=data_input, model="text-embedding-ada-002").data[0].embedding

    else:
        print("none")


def img_create(prompt="a nice house on the beach", download_path=""):
    # to open, must download
    my_url = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024").data[0].url
    if download_path:
        my_image = requests.get(my_url)
        if my_image.status_code == 200:
            with open(download_path, 'wb') as f:
                f.write(my_image.content)
        else:
            print("Failed to retrieve image")
    return my_url


def img_to_text(img_url="", img_base64="", prompt="What’s in this image?", print_out=True):
    if img_url:
        img_desc_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": img_url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=500,
        )
        if print_out:
            print(img_desc_response.choices[0].message.content)
        return img_desc_response.choices[0].message.content
    elif img_base64:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
        }
        payload = {
            "model": "gpt-4-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        img_desc_response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if print_out:
            print(img_desc_response.json()["choices"][0]["message"]["content"])
        return img_desc_response.json()["choices"][0]["message"]["content"]
    else:
        return ValueError


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string


def table_to_text(table=None, prompt="describe this table in plain text. "
                                     "be as precise as possible. spare no detail. "
                                     "what is in this table?", print_out=True):
    if table is not None:
        response = gpt4_new(f"{prompt} TABLE: {table}")
        if print_out:
            print(response)
        return response
    else:
        return ValueError


if __name__ == "__main__":
    #img_create("a skier in the swiss alps", download_path="skier.png")
    #img_to_text(img_base64=encode_image_to_base64("skier.png"))
    #print(image_to_base64("skier.png"))
    #print(vectorize_data("test string"))
    while True:
        print(gpt4_new(input("Prompt: ")))
