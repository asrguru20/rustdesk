# Writes the Interlan server, key and app name into hbb_common before a build.
# hbb_common is an upstream submodule, so it is patched in CI instead of being forked.
import os
import re
import sys

PATH = "libs/hbb_common/src/config.rs"

server = os.environ.get("RENDEZVOUS_SERVER", "").strip()
key = os.environ.get("RS_PUB_KEY", "").strip()
app_name = os.environ.get("INTERLAN_APP_NAME", "").strip()
if not (server and key and app_name):
    sys.exit("::error::RENDEZVOUS_SERVER, RS_PUB_KEY (repository secrets) and INTERLAN_APP_NAME must all be set")

with open(PATH, encoding="utf-8", newline="") as f:
    src = f.read()

replacements = [
    (r'^pub const RENDEZVOUS_SERVERS: &\[&str\] = &\[.*?\];',
     f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{server}"];'),
    (r'^pub const RS_PUB_KEY: &str = ".*?";',
     f'pub const RS_PUB_KEY: &str = "{key}";'),
    (r'(pub static ref APP_NAME: RwLock<String> = RwLock::new\()"RustDesk"(\.to_owned\(\)\);)',
     None),
]
for pattern, value in replacements:
    if value is None:
        src, n = re.subn(pattern, lambda m: f'{m.group(1)}"{app_name}"{m.group(2)}', src, flags=re.M)
    else:
        src, n = re.subn(pattern, lambda _: value, src, flags=re.M)
    if n != 1:
        sys.exit(f"::error::config.rs layout changed, pattern matched {n} times: {pattern}")

with open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print(f"Baked server, key and app name {app_name!r} into {PATH}")
