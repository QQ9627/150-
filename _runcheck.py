import io, sys, contextlib
sys.argv = ['check_part.py',
    r'C:/Users/JNPYY/WorkBuddy/2026-09-27-19-27-34/artists-db/data/artists/part-03-a.json',
    r'C:/Users/JNPYY/WorkBuddy/2026-09-27-19-27-34/artists-db/data/artists/part-03-b.json',
    r'C:/Users/JNPYY/WorkBuddy/2026-09-27-19-27-34/artists-db/data/artists/part-03-c.json']
buf = io.StringIO()
with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
    try:
        import runpy
        runpy.run_path(r'C:/Users/JNPYY/WorkBuddy/2026-09-27-19-27-34/artists-db/scripts/check_part.py', run_name='__main__')
    except SystemExit:
        pass
text = buf.getvalue()
with io.open(r'C:/Users/JNPYY/WorkBuddy/2026-09-27-19-27-34/artists-db/_check_out.txt', 'w', encoding='utf-8') as f:
    f.write(text)
print("DONE len=", len(text))
