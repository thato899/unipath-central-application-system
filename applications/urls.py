from django.urls import path
from . import api, privacy

urlpatterns = [
    path("auth/status", api.auth_status),
    path("profile", api.profile_detail),
    path("profile/update", api.profile_update),
    path("universities", api.universities),
    path("courses", api.courses),
    path("courses/<slug:course_id>/matches", api.course_matches),
    path("applications", api.applications),
    path("applications/create", api.create_applications),
    path("applications/<str:application_id>/decision", api.application_decision),
    path("residence", api.residence_applications),
    path("applications/<str:application_id>/residence", api.create_residence_application),
    path("funding-plan", api.funding_plan),
    path("privacy/export", privacy.export_data),
    path("privacy/delete-account", privacy.delete_account),
]
