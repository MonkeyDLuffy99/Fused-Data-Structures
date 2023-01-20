# Python Fused Datastructures Library

This directory contains the our implementation of the paper _Fault Tolerance in Distributed Systems Using Fused Data Structures_.  
It has been developed in a way that exposes a simple, minimal API to other developers wishing to use our library in their applications.

Communication between hosts is performed over **gRPC**: https://grpc.io/

Developers wishing to interface with our library in languages other than Python can easily do by implementing our protocol,  
which can found in `python_fused_datastructures/protos/service.proto`.

## Directory Structure

- `python_fused_datastructures/*`

  > Our self-contained fused datastructures package.
  >
  > Although this is ready to be published to the Python Package Index (PyPI) for other developers to install and use,  
  > we have not done so yet to avoid abetting plagiarism.

- `python_jerasure/*`:

  > Our self-contained adapter package for the Jerasure C/C++ library.  
  > This handles martialing and unmartialing of data between formats expected by Python and Jerasure.

- `examples/*`:

  > Example programs that make use of our fused datastructures package.  
  > These demonstrate the experience for other developers using our libraries from PyPI.  
  > In case of compatibility issues during execution, sample outputs are also included.

## Running the Examples

To simplify the process of installing dependencies, we have included a `Docker` container to run the provided examples.

Please refer to the following instructions:

- Ensure Docker is installed on your system.  
  MacOS guide: https://docs.docker.com/desktop/mac/install/  
  Linux guide: https://docs.docker.com/engine/install/ubuntu/

- Open a terminal window in the root of this project.
- Build the container image:  
  `docker build . -t python-fused-datastructures`

- Run one of the example programs in the container:  
  `docker run python-fused-datastructures list_example.py`  
  `docker run python-fused-datastructures map_example.py`  
  `docker run python-fused-datastructures queue_example.py`

_Please note: the container image will need to be rebuilt if any modifications are made to the example programs._
