from workload_deploy.logs import run_logs


class FakeWL:
    def get_workload_logs(self, wid, *, level, limit):
        return {"data": [{"body": "hello", "level": level, "limit": limit}]}


def test_run_logs_passes_params():
    out = run_logs(FakeWL(), "wl1", level="debug", limit=25)
    assert out["data"][0]["level"] == "debug"
    assert out["data"][0]["limit"] == 25
