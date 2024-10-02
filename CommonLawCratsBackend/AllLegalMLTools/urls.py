from django.urls import path
from .views import CaseSearchView, CaseSummaryView, UploadCaseDocumentOrURLView, LawChatBotView

urlpatterns = [
    # Define your URL patterns here
    path('case-summarizer/', UploadCaseDocumentOrURLView.as_view(), name='case-summarizer'),
    path('case-search-query/', CaseSearchView.as_view(), name='case-search-query'),
    path('case-search-summary/', CaseSummaryView.as_view(), name='case-search-summary'),
    path('lawchatbot/', LawChatBotView.as_view(), name="lawchatbot"),
]