import openai
from openai import OpenAI
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

OVERVIEW_PROMPT = "You will be provided with a partial code base and an issue statement explaining a problem to resolve."

FIX_PROMPT = """
I need you to solve this issue by generating a single patch file that I can apply directly to this repository using git apply. Please respond with a single patch file in the following format.
<patch>
--- a/file.py
+++ b/file.py
@@ -1,27 +1,35 @@
 def euclidean(a, b):
-    while b:
-        a, b = b, a % b
-    return a
+    if b == 0:
+        return a
+    return euclidean(b, a % b)
 
 
 def bresenham(x0, y0, x1, y1):
     points = []
     dx = abs(x1 - x0)
     dy = abs(y1 - y0)
-    sx = 1 if x0 < x1 else -1
-    sy = 1 if y0 < y1 else -1
-    err = dx - dy
+    x, y = x0, y0
+    sx = -1 if x0 > x1 else 1
+    sy = -1 if y0 > y1 else 1
 
-    while True:
-        points.append((x0, y0))
-        if x0 == x1 and y0 == y1:
-            break
-        e2 = 2 * err
-        if e2 > -dy:
+    if dx > dy:
+        err = dx / 2.0
+        while x != x1:
+            points.append((x, y))
             err -= dy
-            x0 += sx
-        if e2 < dx:
-            err += dx
-            y0 += sy
+            if err < 0:
+                y += sy
+                err += dx
+            x += sx
+    else:
+        err = dy / 2.0
+        while y != y1:
+            points.append((x, y))
+            err -= dx
+            if err < 0:
+                x += sx
+                err += dy
+            y += sy
 
+    points.append((x, y))
     return points
</patch>
"""

STEP_BY_STEP = "Let's think step by step."

REVISE_STATEMENT = """
The previous patch was:
{}

However, the previous patch had the following error:
{}

Write a new patch that doesn't have an error.
"""

GEN_OVERVIEW_PROMPT = "You will be provided with a file in a code base and an issue statement explaining a problem to resolve."

GEN_FIX_PROMPT = "I need you to solve this issue by outlining the changes to make. "

def remove_first_and_last_line(text):
    lines = text.splitlines()
    return '\n'.join(lines[1:-1]) if len(lines) > 2 else ''

def join_code(codebase):
    out = ""
    for file in codebase:
        out += "[start of " + file[0] + "]"
        out += file[1]
        out += "[end of " + file[0] + "]\n"
    return out

def get_patch(problem_statement, relevant_code, previous_patch=None, patch_error=None):
    if previous_patch:
        revise_statement = REVISE_STATEMENT.format(previous_patch, patch_error)
        query = OVERVIEW_PROMPT + "\n<issue>\n" + problem_statement + "\n<\issue>\n<code>\n" + relevant_code + "<\code>\n" + FIX_PROMPT + "\n" + revise_statement + "\n" + STEP_BY_STEP
    else:
        query = OVERVIEW_PROMPT + "\n<issue>\n" + problem_statement + "\n<\issue>\n<code>\n" + relevant_code + "<\code>\n" + FIX_PROMPT + STEP_BY_STEP

    messages = [{"role": "user", "content": query}]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    query2 = "Now output just the patch file so that it can be run with the unix patch command. Do not output anything else."
    messages = [{"role": "user", "content": query},
                {"role": "assistant", "content": response.choices[0].message.content},
                {"role": "user", "content": query2}]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content

def get_new_code(problem_statement, code, previous_patch=None, patch_error=None):
    joined_code = join_code(code)
    if previous_patch:
        revise_statement = REVISE_STATEMENT.format(previous_patch, patch_error)
        query = OVERVIEW_PROMPT + "\n<issue>\n" + problem_statement + "\n<\issue>\n<code>\n" + joined_code + "<\code>\n" + GEN_FIX_PROMPT + "\n" + revise_statement + "\n" + STEP_BY_STEP
    else:
        query = OVERVIEW_PROMPT + "\n<issue>\n" + problem_statement + "\n<\issue>\n<code>\n" + joined_code + "<\code>\n" + GEN_FIX_PROMPT + "\n" + STEP_BY_STEP

    messages = [{"role": "user", "content": query}]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    outputs = []
    for file in code:
        query2 = f"Now output just the complete code for the new file {file[0]}. Do not output anything else."
        messages = [{"role": "user", "content": query},
                    {"role": "assistant", "content": response.choices[0].message.content},
                    {"role": "user", "content": query2}]
        response2 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        outputs.append((file[0], response2.choices[0].message.content))
    return outputs