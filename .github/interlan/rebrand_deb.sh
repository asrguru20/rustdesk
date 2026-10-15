#!/bin/bash
# Turns the stock rustdesk .deb into interlandesk. On Linux the client derives its systemd unit,
# process name (pkill / ps patterns) and .desktop name from APP_NAME, so every "rustdesk" path in
# the package has to follow it. The bundled core library keeps its name (librustdesk.so).
# Usage: rebrand_deb.sh <in.deb> <out.deb>
set -euo pipefail

in=$1
out=$2
name=interlandesk
Name=InterlanDesk

work=$(mktemp -d)
p=$work/pkg
dpkg-deb -R "$in" "$p"

mv "$p/usr/share/rustdesk" "$p/usr/share/$name"
mv "$p/usr/share/$name/rustdesk" "$p/usr/share/$name/$name"
mv "$p/usr/share/$name/files/systemd/rustdesk.service" "$p/usr/share/$name/files/systemd/$name.service"
mv "$p/usr/share/applications/rustdesk.desktop" "$p/usr/share/applications/$name.desktop"
mv "$p/usr/share/applications/rustdesk-link.desktop" "$p/usr/share/applications/$name-link.desktop"
find "$p/usr/share/icons" -name 'rustdesk.*' | while read -r f; do
  mv "$f" "$(dirname "$f")/$name.${f##*.}"
done
find "$p/usr/share/polkit-1" -name '*rustdesk*' | while read -r f; do
  mv "$f" "$(dirname "$f")/$(basename "$f" | sed "s/rustdesk/$name/g")"
done

# Text files only: maintainer scripts, unit, .desktop, polkit policy.
grep -rlI -e rustdesk -e RustDesk "$p/DEBIAN" "$p/usr/share/$name/files" "$p/usr/share/applications" "$p/usr/share/polkit-1" \
  | grep -v '/DEBIAN/md5sums$' \
  | xargs -r sed -i -e "s/rustdesk\.com/interlan.app/g" -e "s/rustdesk/$name/g" -e "s/RustDesk/$Name/g"
sed -i -e "s/^Maintainer: .*/Maintainer: Interlan <info@interlan.app>/" \
       -e "s/^Description: .*/Description: InterlanDesk remote support for Interlan/" "$p/DEBIAN/control"

(cd "$p" && find . -path ./DEBIAN -prune -o -type f -printf '%P\0' | xargs -0 md5sum > DEBIAN/md5sums)
dpkg-deb --root-owner-group -b "$p" "$out"
dpkg-deb -I "$out" | sed -n '/Package:/,/Description:/p'
dpkg-deb -c "$out" | grep -E "/usr/share/$name/$name\$|$name.service|$name.desktop"
rm -rf "$work"
