import pytest
import httpx
from simco2.adapters.routing import FixtureRoutingProvider, ORSRoutingProvider
from simco2.domain.errors import RoutingFailure


def test_fixture_not_invented_on_unknown_route():
    r = FixtureRoutingProvider({((0,0), (1,1), "driving-hgv"): (5000, 400)})
    assert r.route((0,0), (1,1), "driving-hgv").distance_m == 5000
    with pytest.raises(RoutingFailure):
        r.route((0,0), (9,9), "driving-hgv")


def test_ors_mocked_without_real_network_or_api_key_leak():
    def mock(request):
        assert request.headers["Authorization"] == "TEST-SECRET"
        return httpx.Response(200, json={"features": [{"properties": {"summary": {
            "distance": 10000, "duration": 900}}, "geometry": {"type": "LineString",
              "coordinates": [[0,0],[1,1]]}}], "metadata": {"engine": {"version": "vX"}}})
    with httpx.Client(transport=httpx.MockTransport(mock)) as client:
        r = ORSRoutingProvider("TEST-SECRET", client=client)
        out = r.route((0, 0), (1,1), "driving-hgv")
        assert out.duration_s == 900
        assert out.provider_version == "vX"
    with pytest.raises(RoutingFailure) as exc:
        ORSRoutingProvider("", client=None)
    assert "SECRET" not in str(exc.value)
