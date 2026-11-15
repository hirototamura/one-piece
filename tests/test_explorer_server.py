"""Exercise the packaged web app over HTTP, including its retained examples."""
import json
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from onepiece import Store
from onepiece.explorer_server import explorer_server

ROOT = Path(__file__).resolve().parents[1]


def test_web_app_serves_current_model_and_examples_without_store_writes():
    store = Store(ROOT / 'projects/balancing-cube/store')
    before = {p: p.read_bytes() for p in store.path.glob('commits/*/*.json')}
    with explorer_server(store, port=0) as server:
        directory = Path(server.RequestHandlerClass.keywords['directory'])
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        origin = f'http://127.0.0.1:{server.server_port}'
        try:
            def get(path):
                with urlopen(origin + path) as response:
                    return response.read()
            html = get('/').decode()
            assert 'id="design-coverage"' not in html
            assert 'id="graph-version"' not in html
            assert 'graph-object-picker' in html
            models = json.loads(get('/data/models.json'))
            assert models['balancing_cube']['counts']['obligations'] == 19
            assert models['balancing_cube']['operating_parameters']['hold_interval_s'] == 10
            assert models['eclss']['scenario'] and models['scrubber']['scenario']
            assert models['generated_from']['bundled_comparison_source']['sha256']
            assert b'font-size: 12.8px' in get('/styles.css')
            with pytest.raises(HTTPError) as error:
                urlopen(Request(origin + '/', data=b'{}', method='POST'))
            assert error.value.code == 501
            with pytest.raises(HTTPError):
                get('/store/commits/')
        finally:
            server.shutdown()
            thread.join(timeout=5)
    assert not directory.exists()
    assert before == {p: p.read_bytes() for p in store.path.glob('commits/*/*.json')}
