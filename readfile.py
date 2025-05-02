import boto3
import openai
import iov
from PyPDF2 import PdfReader

def read_s3_pdf(bucket_name, common_string, batch size):
    access_key = 'NA'
    secret_key = 'NA'

    s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    
    try:
        # List objects in the S3 bucket that match the common string
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=common_string)
        
        if 'Contents' in response:
            # Iterate through the objects and read their content
            for obj in response['Contents']:
                file_name = obj['Key']
                # Read the file content
                response = s3.get_object(Bucket=bucket_name, Key=file_name)
                file_content = response['Body'].read()

                # Process the PDF content
                # Initialize variables

                pdf_file = io.BytesIO(file_content)
                pdf_reader = PdfReader(pdf_file)
                total_pages = pdf_reader.numPages
                current_page = 0
                num_pages = len(pdf_reader.pages)
                print(f"File: {file_name}, Number of pages: {num_pages}")
                # for page_num in range(num_pages):
                #     page = pdf_reader.pages[page_num]
                #     print(f"Page {page_num + 1}:\n{page.extract_text()}\n")
                while current_page < total_pages:
                    # Create a batch of text
                    text_batch = ''
                    while current_page < total_pages and len(text_batch) < batch_size:
                        page = pdf_reader.getPage(current_page)
                        text_batch += page.extractText()
                        current_page += 1

                    yield text_batch

                pdf_file.close()                

                def analyze_text_batch(text_batch):
                    # Make an API call to analyze the text batch
                    response = openai.Completion.create(
                    engine="davinci",
                    prompt=text_batch,
        max_tokens=50,  # Adjust as needed
        n = 1  # You can request multiple completions for more insights
    )
    return response.choices[0].text        

        else:
            print(f"No files found in bucket '{bucket_name}' with the common string '{common_string}'")
        
    except Exception as e:
        print(f"Error reading files from bucket '{bucket_name}': {e}")


# Example usage:
bucket_name = 'policydocumentschiesta'
common_string = 'Cochlear'  # Specify the common string in file names
batch_size = 4000

read_s3_pdf(bucket_name, common_string, batch_size)
