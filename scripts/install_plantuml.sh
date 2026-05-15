sudo tee /usr/local/bin/plantuml >/dev/null <<'EOF'
#!/usr/bin/env bash
exec java -jar ${HOME}/bin/plantuml.jar "$@"
EOF

sudo chmod +x /usr/local/bin/plantuml
