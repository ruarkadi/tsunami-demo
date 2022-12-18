FROM adoptopenjdk/openjdk13:debianslim

# Install dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates

WORKDIR /usr/tsunami/repos

RUN git clone --depth 1 "https://github.com/google/tsunami-security-scanner-plugins"

WORKDIR /usr/tsunami/repos/tsunami-security-scanner-plugins/google
RUN chmod +x build_all.sh \
    && ./build_all.sh

RUN mkdir /usr/tsunami/plugins \
    && cp build/plugins/*.jar /usr/tsunami/plugins

WORKDIR /usr/repos

RUN git clone --depth 1 "https://github.com/google/tsunami-security-scanner"

WORKDIR /usr/repos/tsunami-security-scanner

RUN ./gradlew shadowJar \
    && cp $(find "./" -name 'tsunami-main-*-cli.jar') /usr/tsunami/tsunami.jar \
    && cp ./tsunami.yaml /usr/tsunami

FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends nmap ncrack\
    ca-certificates python3 python3-pip python-is-python3 default-jre\
    && apt-get clean \
    && mkdir logs/

COPY --from=0 /usr/tsunami .

COPY tsunami-restapi/ .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]

CMD [ "tsunami-restapi.py" ]

