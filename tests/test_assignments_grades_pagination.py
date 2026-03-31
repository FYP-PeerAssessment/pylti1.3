import unittest

from pylti1p3.assignments_grades import AssignmentsGradesService
from pylti1p3.lineitem import LineItem


class FakeServiceConnector:
    def __init__(self, pages):
        self.pages = pages
        self.requests = []

    def get_paginated_data(self, scopes, url, *args, **kwargs):
        self.requests.append((tuple(scopes), url, kwargs))
        yield from self.pages

    def make_service_request(self, scopes, url, **kwargs):
        self.requests.append((tuple(scopes), url, kwargs))
        return {
            "body": {
                "id": url + "/1",
                "scoreMaximum": 100.0,
                "label": "Score",
            },
            "headers": {},
            "next_page_url": None,
        }


class TestAssignmentsGradesPagination(unittest.TestCase):
    def setUp(self):
        self.service_data = {
            "scope": [
                "https://purl.imsglobal.org/spec/lti-ags/scope/score",
                "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
                "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
                "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly",
            ],
            "lineitems": "http://canvas.docker/api/lti/courses/1/line_items",
            "lineitem": "http://canvas.docker/api/lti/courses/1/line_items/1",
        }

    def test_get_lineitems_reads_all_pages(self):
        connector = FakeServiceConnector(
            [
                {
                    "body": [{"id": "1", "label": "One", "scoreMaximum": 100.0}],
                    "headers": {},
                    "next_page_url": "next",
                },
                {
                    "body": [{"id": "2", "label": "Two", "scoreMaximum": 100.0}],
                    "headers": {},
                    "next_page_url": None,
                },
            ]
        )
        ags = AssignmentsGradesService(connector, self.service_data)

        self.assertEqual(
            [item["id"] for item in ags.get_lineitems()],
            ["1", "2"],
        )

    def test_get_grades_reads_all_pages(self):
        connector = FakeServiceConnector(
            [
                {"body": [{"resultScore": 10}], "headers": {}, "next_page_url": "next"},
                {"body": [{"resultScore": 20}], "headers": {}, "next_page_url": None},
            ]
        )
        ags = AssignmentsGradesService(connector, self.service_data)

        self.assertEqual(
            [grade["resultScore"] for grade in ags.get_grades()],
            [10, 20],
        )

    def test_find_or_create_lineitem_supports_predicate(self):
        connector = FakeServiceConnector(
            [
                {
                    "body": [
                        {
                            "id": "http://canvas.docker/api/lti/courses/1/line_items/2",
                            "resourceId": "resource-2",
                            "label": "Second",
                            "scoreMaximum": 100.0,
                        }
                    ],
                    "headers": {},
                    "next_page_url": None,
                }
            ]
        )
        ags = AssignmentsGradesService(connector, self.service_data)
        lineitem = LineItem()
        lineitem.set_label("Unused").set_score_maximum(100)

        result = ags.find_or_create_lineitem(
            lineitem,
            condition=lambda item: item.get("resourceId") == "resource-2",
        )

        self.assertEqual(result.get_id(), "http://canvas.docker/api/lti/courses/1/line_items/2")

    def test_create_lineitem_posts_to_lineitems_endpoint(self):
        connector = FakeServiceConnector([])
        ags = AssignmentsGradesService(connector, self.service_data)
        lineitem = LineItem()
        lineitem.set_label("Score").set_score_maximum(100)

        created = ags.create_lineitem(lineitem)

        self.assertEqual(created.get_id(), "http://canvas.docker/api/lti/courses/1/line_items/1")
        self.assertEqual(connector.requests[0][1], self.service_data["lineitems"])
