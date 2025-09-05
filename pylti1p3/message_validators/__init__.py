from .deep_link import DeepLinkMessageValidator as DeepLinkMessageValidator
from .resource_message import ResourceMessageValidator as ResourceMessageValidator
from .privacy_launch import PrivacyLaunchValidator as PrivacyLaunchValidator
from .submission_review import SubmissionReviewLaunchValidator as SubmissionReviewLaunchValidator


def get_validators():
    return [
        DeepLinkMessageValidator(),
        ResourceMessageValidator(),
        PrivacyLaunchValidator(),
        SubmissionReviewLaunchValidator(),
    ]
