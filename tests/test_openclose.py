import sys, archmage.cli, pathlib, tempfile, errno, shutil, contextlib


@contextlib.contextmanager
def TempDir():
    tmpdir = tempfile.mkdtemp()
    try:
        yield pathlib.Path(tmpdir)
    finally:
        try:
            shutil.rmtree(tmpdir)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise


def test_extract():
    with TempDir() as tmpdir:
        t = tmpdir / "example_html"

        sys.argv = ["extract", "tests/example.chm", t]
        archmage.cli.main()

        for f in ["index.html", "page 1.html", "page 2.html"]:
            assert (t / f).exists()

        assert "Page 1" in (t / "page 1.html").read_text()


def test_render_extracted():
    with TempDir() as tmpdir:
        t = tmpdir / "example_html"

        sys.argv = ["extract", "tests/example", t]
        archmage.cli.main()

        for f in ["index.html", "page 1.html"]:
            assert (t / f).exists()
