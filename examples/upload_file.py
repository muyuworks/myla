import openai

openai.api_key = "sk-"
openai.base_url = "http://localhost:2000/api/v1/"

openai.files.create(
    file=open("./examples/upload_file.py", 'rb'),
    purpose="assistants",
    extra_body={"vector_column_name": "query", "anothor_meta": "another_value"}
)

files = openai.files.list(purpose="assistants")

print(files)