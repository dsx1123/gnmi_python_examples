FROM ubuntu:22.04
RUN apt update -qq && apt install -y python3 python3-dev python3-pip git && apt clean
RUN python3 -m pip install pyats  \
                    robotframework==6.1.1 \
                    genie \
                    pyats \
                    pyats.robot \
                    genie.libs.robot \
                    pyyaml --proxy http://proxy.esl.cisco.com
