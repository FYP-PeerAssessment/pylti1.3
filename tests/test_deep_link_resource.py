import unittest
from pylti1p3.deep_link_resource import DeepLinkResource
from pylti1p3.lineitem import LineItem


class TestDeepLinkResource(unittest.TestCase):
    def test_to_dict_omits_custom_when_empty_or_unset(self):
        resource = DeepLinkResource().set_title("Test title").set_url("https://tool.example/launch")
        self.assertNotIn("custom", resource.to_dict())

        resource_with_empty_custom = (
            DeepLinkResource()
            .set_title("Test title")
            .set_url("https://tool.example/launch")
            .set_custom_params({})
        )
        self.assertNotIn("custom", resource_with_empty_custom.to_dict())

    def test_to_dict_includes_custom_when_non_empty(self):
        custom_params = {"custom_param": "custom_value"}
        resource = (
            DeepLinkResource()
            .set_title("Test title")
            .set_url("https://tool.example/launch")
            .set_custom_params(custom_params)
        )

        self.assertEqual(resource.to_dict().get("custom"), custom_params)

    def test_to_dict_omits_empty_submission_review_custom(self):
        lineitem = LineItem(
            {
                "scoreMaximum": 100,
                "submissionReview": {"reviewableStatus": ["Pending"], "custom": {}},
            }
        )
        resource = DeepLinkResource().set_title("Test title").set_url("https://tool.example/launch")
        resource.set_lineitem(lineitem)

        resource_dict = resource.to_dict()
        submission_review = resource_dict.get("lineItem", {}).get("submissionReview")

        self.assertEqual(submission_review, {"reviewableStatus": ["Pending"]})
