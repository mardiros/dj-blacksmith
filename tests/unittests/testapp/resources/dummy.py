from blacksmith import PathInfoField, Request, Response, register


class Get(Request):
    name: str = PathInfoField()


class Dummy(Response):
    name: str
    id: str


register(
    client_name="dummy",
    resource="dummies",
    service="dummy",
    version="v1",
    path="/dummies",
    contract={"GET": (Get, Dummy)},
)
