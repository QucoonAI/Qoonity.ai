import boto3, json
import os
from qooneous import qoonity_head
from botocore.exceptions import ClientError

session = boto3.Session()
bedrock = session.client(service_name='bedrock-runtime', region_name="us-east-1")
modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"
memory_list = []

# Function to fetch a response from the model
def get_completion(prompt, system_prompt=None):
    inference_config = {
        "temperature": 0.0,
        "maxTokens": 2000,
    }
    converse_api_params = {
        "modelId": modelId,
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": inference_config
    }
    if system_prompt:
        converse_api_params["system"] = [{"text": system_prompt}]
    try:
        response = bedrock.converse(**converse_api_params)
        text_content = response['output']['message']['content'][0]['text']
        return text_content

    except ClientError as err:
        message = err.response['Error']['Message']
        print(f"A client error occurred: {message}")
        return None

# Load memory from file if it exists and is valid
file_path = 'memory.txt'
if os.path.exists(file_path):
    try:
        with open(file_path, 'r') as file:
            memory_list = json.load(file)
            print(f"Memory loaded from {file_path}")
    except json.JSONDecodeError:
        print("Error: memory.txt is empty or contains invalid JSON. Starting fresh.")
        memory_list = [] 
else:
    print("No memory file found, starting fresh.")

while True:
    try:
        prompt = input("Enter your prompt (or type 'exit' to quit): ")
        if prompt.lower() in ["exit", "quit"]:
            print("\nExiting...")
            break

        system_prompt = qoonity_head
        
        # Use the loaded memory when generating the completion
        response = get_completion(prompt + " " + str(memory_list), system_prompt)
        
        if response:  # Only process if the response is valid
            memory_list.append(f"memory: {response}")
            print("Response:", response)
            #print("Memory:", memory_list)

            # Save memory to a file
            with open(file_path, 'w') as file:
                json.dump(memory_list, file, indent=4)
            
            print(f"Memory successfully written to {file_path}")
        else:
            print("No response from the model. Please try again.")
                
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"An error occurred: {e}")




# answer = get_completion(prompt, system_prompt)
# print(answer)
# message_list = []

# initial_message = {
#     "role": "user",
#     "content": [
#         { "text": f"I want to build a edtech platform using {qoonity_head}" } 
#     ],
#     # "role": "assistant",
#     # "content": [
#     #     { "text": qoonity_head }
#     # ],
# }

# message_list.append(initial_message)

# response = bedrock.converse(
#     modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
#     messages=message_list,
#     inferenceConfig={
#         "maxTokens": 2000,
#         "temperature": 0
#     },
# )

# response_message = response['output']['message']
# print(json.dumps(response_message, indent=4))

