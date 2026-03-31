import unittest

from pylti1p3.roles import StudentRole, TeacherRole


class TestRoles(unittest.TestCase):
    def test_context_roles_take_precedence_over_institution_roles(self):
        jwt_body = {
            "https://purl.imsglobal.org/spec/lti/claim/roles": [
                "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor",
                "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner",
            ]
        }

        self.assertTrue(StudentRole(jwt_body).check())
        self.assertFalse(TeacherRole(jwt_body).check())

    def test_membership_roles_are_parsed_as_context_roles(self):
        jwt_body = {
            "https://purl.imsglobal.org/spec/lti/claim/roles": [
                "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor"
            ]
        }

        self.assertTrue(TeacherRole(jwt_body).check())
