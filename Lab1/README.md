File-based client-server example (Python)

Description
-----------
This small project implements a client and server that communicate via two files
in the repository root (no subfolder):

- `dane` - client writes a single integer request here
- `wyniki` - server writes the computed result here

The server runs in a loop (busy-waiting with a small sleep) checking `dane`.
When it finds an integer it computes a small polynomial and writes the result to
`wyniki`. For demonstration purposes the server does NOT clear files after
processing: both `dane` and `wyniki` will retain the last request/result so
you can show them to your teacher. The client still clears `wyniki` before
sending a new request to avoid reading an older result, but does NOT clear it
after reading.

Why Python?
-----------
Python is concise and cross-platform. It has simple file APIs and is ideal for
this educational, file-polling IPC example. JavaScript (Node.js) is also
possible, but Python requires no additional setup for most students.

How to run
----------
1. Start the server (run once and leave it running):

   python3 server.py

2. In another terminal, run the client. You can run the client multiple times:

   python3 client.py

Notes
-----
- Always start `server.py` first.
- The code uses simple busy-waiting with a 0.1s sleep to reduce CPU usage.
- We assume only one client runs at a time.
-- If you see stale results, delete or empty files `dane` and `wyniki` in the
   repository root before running the client.
