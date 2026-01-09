"""URL configuration for integrations app."""
from django.urls import path
from .views import (
    GitLabIntegrationView, GitLabProjectView, GitLabBranchesView, GitLabTagsView,
    ALMIntegrationView, ALMTestSetsView, ALMTestCasesView, ALMSyncView,
    ArtifactRepoIntegrationView, ArtifactRepoSearchView, ArtifactRepoVersionsView
)

urlpatterns = [
    # GitLab
    path('gitlab/', GitLabIntegrationView.as_view(), name='gitlab-test'),
    path('gitlab/projects/<str:project_id>/', GitLabProjectView.as_view(), name='gitlab-project'),
    path('gitlab/projects/<str:project_id>/branches/', GitLabBranchesView.as_view(), name='gitlab-branches'),
    path('gitlab/projects/<str:project_id>/tags/', GitLabTagsView.as_view(), name='gitlab-tags'),
    
    # ALM
    path('alm/', ALMIntegrationView.as_view(), name='alm-test'),
    path('alm/projects/<str:project_id>/test-sets/', ALMTestSetsView.as_view(), name='alm-test-sets'),
    path('alm/test-sets/<str:test_set_id>/cases/', ALMTestCasesView.as_view(), name='alm-test-cases'),
    path('alm/sync/', ALMSyncView.as_view(), name='alm-sync'),
    
    # Artifact Repository
    path('artifacts/', ArtifactRepoIntegrationView.as_view(), name='artifact-test'),
    path('artifacts/search/', ArtifactRepoSearchView.as_view(), name='artifact-search'),
    path('artifacts/versions/', ArtifactRepoVersionsView.as_view(), name='artifact-versions'),
]
