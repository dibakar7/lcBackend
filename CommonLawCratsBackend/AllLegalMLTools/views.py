import os
import time
import requests
import pandas as pd
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv
load_dotenv()

from .helper_functions_llm import extract_text_from_pdf, clean_text, split_text_into_token_chunks, generate_embeddings, index_embeddings, generate_summary, retrieve_similar_chunks, download_pdf_from_url
from rest_framework.permissions import AllowAny



# Below section is for case summarizer
class UploadCaseDocumentOrURLView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format = None):
        caseDocument = request.FILES.get('pdf_file')
        caseURL = request.data.get('url')

        if caseDocument or caseURL:
            if caseDocument:
                text = extract_text_from_pdf(caseDocument)
            else:
                caseURLPdf_stream = download_pdf_from_url(caseURL)
                text = extract_text_from_pdf(caseURLPdf_stream)

            cleaned_text = clean_text(text)
            chunks = split_text_into_token_chunks(cleaned_text, 4000)

            try:
                embeddings = generate_embeddings(chunks)
                index = index_embeddings(embeddings)

                query_embedding = generate_embeddings([cleaned_text[:8191]])[0]  
                similar_chunks = retrieve_similar_chunks(index, query_embedding, chunks)

                summary = generate_summary(similar_chunks)

                # here we need to return generated summary to frontend through api endpoint
                return Response({'summary': summary}, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            return Response({'error': 'Invalid file type and void url'})
        
# Below classes both together is for handling case search and generating summary functionality
class CaseSearchView(APIView):
    # in development phase it is made that all can access this class view but before production make sure to change
    # AllowAny to IsAuthenticated or other built-in classes
    permission_classes = [AllowAny]      

    def post(self, request, format=None):
        case_search_query = request.data.get('search_query')
        file_path = os.path.join(settings.BASE_DIR, 'AllLegalMLTools', 'updated_merged_dataset.csv')
        merged_df = pd.read_csv(file_path)

        if case_search_query:
            case_search_query = case_search_query.lower()
            results = merged_df[merged_df['details'].str.contains(case_search_query, na=False)]

            if results.empty:
                return Response({'message': f"No results found for '{case_search_query}'"}, status=status.HTTP_200_OK)

            response_data = [
                {
                    'case_title': row['Case Title'],
                    'case_no': row['Case No'],
                    'pdf_link': row['PDF Link'],
                    'index' : idx
                }
                for idx, row in results.iterrows()
            ]

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            return Response({'error': 'Invalid query'}, status=status.HTTP_400_BAD_REQUEST)
        
class CaseSummaryView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format = None):
        case_index = request.data.get('index')
        file_path = os.path.join(settings.BASE_DIR, 'AllLegalMLTools', 'updated_merged_dataset.csv')
        merged_df = pd.read_csv(file_path)

        if case_index is not None:
            try:
                case_index = int(case_index)
                results = merged_df.iloc[case_index]

                pdf_url = results['PDF Link']
                response_data = []
                try:
                    pdf_stream = download_pdf_from_url(pdf_url)
                    text = extract_text_from_pdf(pdf_stream)
                    cleaned_text = clean_text(text)
                    chunks = split_text_into_token_chunks(cleaned_text, 8191)

                    embeddings = generate_embeddings(chunks)
                    index = index_embeddings(embeddings)

                    query_embedding = generate_embeddings([cleaned_text[:8191]])[0] 
                    similar_chunks = retrieve_similar_chunks(index, query_embedding, chunks)

                    summary = generate_summary(similar_chunks)
                    response_data.append({
                        'Case Title': results['Case Title'],
                        'Case No': results['Case No'],
                        'Judges': results['Judges'],
                        'Decision Date': results['Decision Date_left'],
                        'Disposal Nature': results['Disposal Nature'],
                        'PDF Link': results['PDF Link'],
                        'Summary': summary
                    })
                    return Response(response_data, )
                except Exception as e:
                    return Response({'error': f"Failed to process:'{str(e)}'"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            except Exception as e:
                return Response({'error': f"Case not found"}, status=status.HTTP_404_NOT_FOUND)
            
        else:
            return Response({'error': 'case_index is null'}, status=status.HTTP_400_BAD_REQUEST)
        
class LawChatBotView(APIView):
    permission_classes = [AllowAny]
    max_retries = 5  # Set the maximum number of retries
    retry_delay = 10  # Time to wait between retries (in seconds)

    def make_submit_query_call(self, query):

        url = "https://7tmdf4lcsil23zs6hcbaptmo5q0dgvla.lambda-url.us-east-1.on.aws/submit_query"

        response = requests.post(url, json={"query_text": query})
        response.raise_for_status()
        response_data = response.json()
        return response_data["query_id"]
        
    def get_query_response(self, unique_id):

        base_url = "https://7tmdf4lcsil23zs6hcbaptmo5q0dgvla.lambda-url.us-east-1.on.aws/get_query"
        url = f"{base_url}?query_id={unique_id}"
        
        # for _ in range(max_retries):
        for attempt in range(self.max_retries):
            response = requests.get(url)
            response.raise_for_status()
            response_data = response.json()

            # Check if the response is complete
            if response_data.get("is_complete"):
                return response_data  # Return the complete response

            # If not complete, wait before the next attempt
            time.sleep(self.retry_delay)

        return None  # Return None if the response is not complete after max retries

    def post(self, request, format=None):
        query = request.data.get('query')
        
        try:
            query_id = self.make_submit_query_call(query)
            answer = self.get_query_response(query_id)

            if answer is not None:
                return Response(answer, status=status.HTTP_200_OK)
            else:
                return Response({"error": "query did not complete in time."}, status=status.HTTP_408_REQUEST_TIMEOUT)

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)