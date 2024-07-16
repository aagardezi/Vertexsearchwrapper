import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason, GenerationConfig, Tool
import vertexai.preview.generative_models as generative_models
from vertexai.preview.generative_models import grounding
from google.cloud import pubsub_v1

def generate(current_project, request):
  vertexai.init(project=current_project, location="us-central1")
  model = GenerativeModel("gemini-1.5-pro-001")
  responses = model.generate_content(
      [""f"{request}"""],
      generation_config=generation_config,
      safety_settings=safety_settings,
      stream=True,
  )

  qna=''

  for response in responses:
    qna += response.text
  return qna

def generate_grounded(current_project, request):
  vertexai.init(project=current_project, location="us-central1")
  model = GenerativeModel("gemini-1.5-pro-001")

  tool = Tool.from_retrieval(
    grounding.Retrieval(grounding.VertexAISearch(datastore=f"projects/{current_project}/locations/global/collections/default_collection/dataStores/bailiilegaldemo-ds_1711929181751"))
    )
  response = model.generate_content(
    request,
    tools=[tool],
    generation_config=GenerationConfig(
        temperature=0.0,
    ),
)

  print(response)
  return response.text

def generate_file_response(current_project, request, filename):
  vertexai.init(project=current_project, location="us-central1")
  model = GenerativeModel("gemini-1.5-pro-001")
  responses = model.generate_content(
      [Part.from_uri(mime_type=filename.split()[1], uri=filename.split()[0]), ""f"{request}"""],
      generation_config=generation_config,
      safety_settings=safety_settings,
      stream=True,
  )

  fileresponse = ''  
  for response in responses:
    fileresponse += response.text
  return fileresponse


generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

def publish_gemini_message(current_project, topic_id, request, filename, space_name):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(current_project, topic_id)
    future = publisher.publish(topic_path, request.encode("utf-8"), request_type="File", uri=filename.split()[0], mime_type=filename.split()[1], spacename=space_name)
    print(future.result())

def publish_gemini_compare_message(current_project, topic_id, request, filename1, filename2, space_name):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(current_project, topic_id)
    future = publisher.publish(topic_path, request.encode("utf-8"), request_type="Compare", uri1=filename1.split()[0], mime_type1=filename1.split()[1], uri2=filename2.split()[0], mime_type2=filename2.split()[1], spacename=space_name)
    print(future.result())

def publish_gemini_assess_claim(current_project, topic_id, request, filename1, filename2, filename3, space_name):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(current_project, topic_id)
    future = publisher.publish(topic_path, request.encode("utf-8"), request_type="Claim", uri1=filename1.split()[0], mime_type1=filename1.split()[1], uri2=filename2.split()[0], mime_type2=filename2.split()[1], uri2=filename3.split()[0], mime_type2=filename3.split()[1], spacename=space_name)
    print(future.result())


