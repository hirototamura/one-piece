from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from one_piece_connectors.ssos import ingest_ssos_repo


class SSOSErrorIngestTest(unittest.TestCase):
    def test_ingest_ssos_repo_extracts_packages_and_topics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            package_dir = root / "thermal_manager"
            package_dir.mkdir()
            (package_dir / "package.xml").write_text(
                "<package><name>thermal_manager</name></package>",
                encoding="utf-8",
            )
            (package_dir / "node.py").write_text(
                "pub = self.create_publisher(String, '/thermal/heat_load', 10)\n"
                "sub = self.create_subscription(String, '/thermal/heat_load', cb, 10)\n",
                encoding="utf-8",
            )

            graph = ingest_ssos_repo(root)

            self.assertEqual(len(graph["elements"]), 1)
            self.assertEqual(graph["elements"][0]["discipline"], "thermal")
            self.assertEqual(len(graph["interfaceControlDocuments"]), 1)
            self.assertEqual(graph["designArtifacts"][0]["kind"], "source_repo")


if __name__ == "__main__":
    unittest.main()
