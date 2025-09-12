import json
import typing as t
from .exception import LtiException


TExtaClaims = t.Mapping[str, t.Any]


class Grade:
    _score_given: float | None = None
    _score_maximum: float | None = None
    _activity_progress: str | None = None
    _grading_progress: str | None = None
    _timestamp: str | None = None
    _user_id: str | None = None
    _comment: str | None = None
    _extra_claims: TExtaClaims | None = None

    def _validate_score(self, score_value) -> str | None:
        if not isinstance(score_value, (int, float)):
            return "score must be integer or float"
        if score_value < 0:
            return "score must be positive number (including 0)"
        return None

    def get_score_given(self) -> float | None:
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#scoregiven-and-scoremaximum
        """
        return self._score_given

    def set_score_given(self, value: float) -> "Grade":
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#scoregiven-and-scoremaximum
        """
        err_msg = self._validate_score(value)
        if err_msg is not None:
            raise LtiException("Invalid scoreGiven value: " + err_msg)
        self._score_given = value
        return self

    def get_score_maximum(self) -> float | None:
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#scoregiven-and-scoremaximum
        """
        return self._score_maximum

    def set_score_maximum(self, value: float) -> "Grade":
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#scoregiven-and-scoremaximum
        """
        err_msg = self._validate_score(value)
        if err_msg is not None:
            raise LtiException("Invalid scoreMaximum value: " + err_msg)
        self._score_maximum = value
        return self

    def get_activity_progress(self) -> str | None:
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#activityprogress
        """
        return self._activity_progress

    def set_activity_progress(self, value: str) -> "Grade":
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#activityprogress
        """
        self._activity_progress = value
        return self

    def get_grading_progress(self) -> str | None:
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#gradingprogress
        """
        return self._grading_progress

    def set_grading_progress(self, value: str) -> "Grade":
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#gradingprogress
        """
        self._grading_progress = value
        return self

    def get_timestamp(self) -> str | None:
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#timestamp
        """
        return self._timestamp

    def set_timestamp(self, value: str) -> "Grade":
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#timestamp
        """
        self._timestamp = value
        return self

    def get_user_id(self) -> str | None:
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#userid-0
        """
        return self._user_id

    def set_user_id(self, value: str) -> "Grade":
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#userid-0
        """
        self._user_id = value
        return self

    def get_comment(self) -> str | None:
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#comment-0
        """
        return self._comment

    def set_comment(self, value: str) -> "Grade":
        """
        https://www.imsglobal.org/spec/lti-ags/v2p0/#comment-0
        """
        self._comment = value
        return self

    def set_extra_claims(self, value: TExtaClaims) -> "Grade":
        self._extra_claims = value
        return self

    def get_extra_claims(self) -> TExtaClaims | None:
        return self._extra_claims

    def get_value(self) -> str:
        data = {
            "scoreGiven": self._score_given,
            "scoreMaximum": self._score_maximum,
            "activityProgress": self._activity_progress,
            "gradingProgress": self._grading_progress,
            "timestamp": self._timestamp,
            "userId": self._user_id,
            "comment": self._comment,
        }
        if self._extra_claims is not None:
            data.update(self._extra_claims)

        return json.dumps({k: v for k, v in data.items() if v is not None})
