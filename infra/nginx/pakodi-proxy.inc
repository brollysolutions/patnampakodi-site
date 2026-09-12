# Include at server scope in the existing HTTPS site, replacing its old
# application location blocks. Keep its certificate and HTTP redirect settings.
access_log off;
client_max_body_size 5m;

location / {
    proxy_pass http://127.0.0.1:3502;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_set_header Host patnampakodi.com;
    proxy_set_header X-Forwarded-Host patnampakodi.com;
    proxy_set_header X-Forwarded-Proto https;
    # Overwrite client-supplied addresses; do not append their XFF chain.
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Forwarded "";
}
