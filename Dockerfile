# #------------------------------------------------------------------------------
# FROM alpine as envision

# RUN apk --no-cache add \
#     npm

# COPY /web /work

# WORKDIR /work/envision

# RUN npm run build

#------------------------------------------------------------------------------
FROM alpine

RUN apk --no-cache add \
    alpine-base \
    bash \
    clang \
    go \
    htop \
    nginx \
    npm \
    nodejs \
    openjdk17 \
    openssh \
    openssl \
    postgresql \
    protoc \
    py3-pip \
    python3 \
    sqlite \
    memcached \
    redis \
    supervisor \
    tree

ADD https://github.com/just-containers/s6-overlay/releases/download/v3.1.0.1/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v3.1.0.1/s6-overlay-aarch64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-aarch64.tar.xz
ENTRYPOINT ["/init"]

RUN npm i -g \
    mountebank \
    mountebank-grpc-mts

RUN pip3 install \
    PyYAML


ENV PATH=/envelope/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    GOBIN=/envelope/bin \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk \
    S6_KEEP_ENV=1 \
    S6_KILL_GRACETIME=500

RUN mkdir /go && \
    go install github.com/google/go-jsonnet/cmd/jsonnet@latest

COPY /root /

# COPY --from=envision /work/envision/build /web/admin

# ngnix, mountebank
EXPOSE 80/tcp 2525/tcp
