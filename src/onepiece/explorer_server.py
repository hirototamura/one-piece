"""Run the packaged Explorer against a generated, immutable local view."""
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from tempfile import TemporaryDirectory

from .explorer import build_explorer


@contextmanager
def explorer_server(store, *, port=8791, **options):
    """Build once at startup; serve only the temporary projection on loopback."""
    with TemporaryDirectory(prefix="onepiece-explorer-") as directory:
        build_explorer(store, directory, bundled_comparisons=True, **options)
        handler = partial(SimpleHTTPRequestHandler, directory=directory)
        with ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
            yield server


def serve_explorer(store, *, port=8791, **options):
    with explorer_server(store, port=port, **options) as server:
        url = f"http://127.0.0.1:{server.server_port}/"
        print(f"Systems Requirements Explorer: {url}", flush=True)
        print("Press Ctrl-C to stop. Restart to load source/model changes.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        return {"url": url, "stopped": True}
