ARG IMAGE_TAG=3.8.5-alpine3.12

FROM python:${IMAGE_TAG}

ARG PKGNAME

ENV PYTHONDONTWRITEBYTECODE=1

COPY . /app-bundle/

RUN set -eu pipefall \
    && sed -i -e 's/http:\/\//https:\/\//g' /etc/apk/repositories \
    && apk update --no-cache \
    && apk add --no-cache --virtual .build-base \
        binutils \
        file \
        gcc \
        g++ \
        make \
        libc-dev \
        musl-dev \
        fortify-headers \
        patch \
    && apk add --no-cache --virtual .pillow-deps \
        freetype-dev \
        openjpeg-dev \
        libimagequant-dev \
        libwebp-dev \
        tiff-dev \
        libpng-dev \
        lcms2-dev \
        libjpeg-turbo-dev \
        libxcb-dev \
        zlib-dev \
    && apk add --no-cache --virtual .pyyaml-deps \
        yaml-dev \
        cython \
    && cd /app-bundle \
    && python3 -B -m pip --no-cache-dir install .[extra] \
    && find /usr/local -depth \
        \( \
            \( -type d -a \( -name test -o -name tests -o -name idle_test -o -name __pycache__ \) \) \
            -o \
            \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.pyd' \) \) \
        \) | xargs rm -rf \
    && apk del --no-cache --clean-protected --purge \
        .build-base \
        .pillow-deps \
        .pyyaml-deps
    
ENTRYPOINT ["/bin/ash"]
