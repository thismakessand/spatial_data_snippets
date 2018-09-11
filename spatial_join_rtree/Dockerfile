FROM python:3.6

# install libspatialindex 1.7.0, dependency for python rtree package
RUN curl -sSL http://download.osgeo.org/libspatialindex/spatialindex-src-1.7.0.tar.gz -o "spatialindex-src-1.7.0.tar.gz" \
    && tar -zxf spatialindex-src-1.7.0.tar.gz \
    && rm spatialindex-src-1.7.0.tar.gz \
    && cd spatialindex-src-1.7.0 \
    && ./configure \
    && make \
    && make install \
    && ldconfig

COPY requirements.txt /${HOME}/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /${HOME}/requirements.txt \
    && rm /${HOME}/requirements.txt

COPY ./test_join ${HOME}/test_join

WORKDIR ${HOME}/test_join

CMD ["python", "main.py"]