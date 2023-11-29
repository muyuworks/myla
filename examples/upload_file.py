import openai

openai.api_key = "sk-"
openai.base_url = "http://localhost:2000/api/v1/"

openai.files.create(
    #file=open("./examples/upload_file.py", 'rb'),
    file=open("./data/myla_test_kb.json", 'rb'),
    purpose="assistants",
    extra_body={"embeddings": "category,query"}
)

files = openai.files.list(purpose="assistants")

print(files)
