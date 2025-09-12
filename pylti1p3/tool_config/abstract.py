from enum import StrEnum
import typing as t
import collections.abc
from abc import ABCMeta, abstractmethod
from ..deployment import Deployment
from ..registration import Registration
from ..request import Request


RequestT = t.TypeVar("RequestT", bound=Request)


class IssuerToClientRelation(StrEnum):
    ONE_CLIENT_ID_PER_ISSUER = "one-issuer-one-client-id"
    MANY_CLIENTS_IDS_PER_ISSUER = "one-issuer-many-client-ids"


class ToolConfAbstract(t.Generic[RequestT]):
    __metaclass__ = ABCMeta
    issuers_relation_types: collections.abc.MutableMapping[str, IssuerToClientRelation] = {}

    def check_iss_has_one_client(self, iss: str) -> bool:
        """
        Two methods check_iss_has_one_client / check_iss_has_many_clients are needed for the the backward compatibility
        with the previous versions of the library (1.4.0 and early) where ToolConfDict supported only client_id per iss.
        Should return False for all new ToolConf-s
        """
        iss_type = self.issuers_relation_types.get(
            iss, IssuerToClientRelation.ONE_CLIENT_ID_PER_ISSUER
        )
        return iss_type == IssuerToClientRelation.ONE_CLIENT_ID_PER_ISSUER

    def check_iss_has_many_clients(self, iss: str) -> bool:
        """
        Should return True for all new ToolConf-s
        """
        iss_type = self.issuers_relation_types.get(
            iss, IssuerToClientRelation.ONE_CLIENT_ID_PER_ISSUER
        )
        return iss_type == IssuerToClientRelation.MANY_CLIENTS_IDS_PER_ISSUER

    def set_iss_has_one_client(self, iss: str):
        self.issuers_relation_types[iss] = (
            IssuerToClientRelation.ONE_CLIENT_ID_PER_ISSUER
        )

    def set_iss_has_many_clients(self, iss: str):
        self.issuers_relation_types[iss] = (
            IssuerToClientRelation.MANY_CLIENTS_IDS_PER_ISSUER
        )

    def find_registration(self, iss: str, *args, **kwargs) -> Registration:
        """
        Backward compatibility method
        """
        return self.find_registration_by_issuer(iss, *args, **kwargs)

    @abstractmethod
    def find_registration_by_issuer(self, iss: str, *args, **kwargs) -> Registration:
        """
        Find registration in case if iss has only one client id, i.e
        in case of { ... "iss": { ... "client_id: "client" ... }, ... } config.

        You may skip implementation of this method in case if all iss in your config could have more than one client id.
        """
        raise NotImplementedError

    @abstractmethod
    def find_registration_by_params(
        self, iss: str, client_id: str, *args, **kwargs
    ) -> Registration:
        """
        Find registration in case if iss has many client ids, i.e
        in case of { ... "iss": [ { ... "client_id: "client1" ... }, { ... "client_id: "client2" ... } ], ... } config.

        You may skip implementation of this method in case if all iss in your config couldn't have more than one
        client id, but it is outdated and not recommended way of storing configuration.
        """
        raise NotImplementedError

    @abstractmethod
    def find_deployment(self, iss: str, deployment_id: str) -> Deployment | None:
        """
        Find deployment in case if iss has only one client id, i.e
        in case of { ... "iss": { ... "client_id: "client" ... }, ... } config.

        You may skip implementation of this method in case if all iss in your config could have more than one client id.
        """
        raise NotImplementedError

    @abstractmethod
    def find_deployment_by_params(
        self, iss: str, deployment_id: str, client_id: str, *args, **kwargs
    ) -> Deployment | None:
        """
        Find deployment in case if iss has many client ids, i.e
        in case of { ... "iss": [ { ... "client_id: "client1" ... }, { ... "client_id: "client2" ... } ], ... } config.

        You may skip implementation of this method in case if all iss in your config couldn't have more than one
        client id, but it is outdated and not recommended way of storing configuration.
        """
        raise NotImplementedError

    def get_jwks(
        self, iss: str | None = None, client_id: str | None = None, **kwargs
    ):
        keys: list[collections.abc.Mapping[str, t.Any]] = []
        if iss:
            if self.check_iss_has_one_client(iss):
                reg = self.find_registration(iss)
            elif self.check_iss_has_many_clients(iss):
                if not client_id:
                    raise Exception("client_id is not specified")
                reg = self.find_registration_by_params(iss, client_id, **kwargs)
            else:
                raise Exception("Invalid issuer relation type")
            keys = reg.get_jwks()
        return {"keys": keys}
