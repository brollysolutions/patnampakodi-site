FROM node:22-bookworm-slim@sha256:83f487e0a63425e5b4d146fb5e5be574bcbe1b7b843d3ebafdd95eaf7767a7e5 AS build
ARG SITE_INDEXABLE=false
ARG DEPLOYMENT_ENV=preview
ENV SITE_INDEXABLE=$SITE_INDEXABLE DEPLOYMENT_ENV=$DEPLOYMENT_ENV
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /repo/apps/web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
COPY packages/contracts/ /repo/packages/contracts/
RUN npm run build

FROM node:22-bookworm-slim@sha256:83f487e0a63425e5b4d146fb5e5be574bcbe1b7b843d3ebafdd95eaf7767a7e5
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3500
WORKDIR /app
COPY --from=build --chown=node:node /repo/apps/web/.next/standalone ./
COPY --from=build --chown=node:node /repo/apps/web/.next/static ./apps/web/.next/static
COPY --from=build --chown=node:node /repo/apps/web/public ./apps/web/public
COPY --from=build /repo/apps/web/licenses ./licenses
USER node
EXPOSE 3500
CMD ["node", "apps/web/server.js"]
