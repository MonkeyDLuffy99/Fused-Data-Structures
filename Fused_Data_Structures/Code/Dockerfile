FROM python:3.8

# Install Poetry dependency manager
RUN pip install "poetry"

# Copy Poetry requirements
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Install Poetry requirements:
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy project files:
COPY . /code

# Build Jerasure library:
RUN cd /code/python_jerasure && make clean && make

# Set Python path
ENV PYTHONPATH "${PYTHONPATH}:/code:/code/python_fused_datastructures:/code/python_jerasure"

# Run example specified in command-line arguments
ENTRYPOINT ["/bin/bash", "-c", "python /code/examples/\"$@\"", "--"]
