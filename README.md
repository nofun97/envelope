# Envelope

Envelope is a framework that makes it easier to develop, test, deploy and
monitor secure container apps.

CAUTION: This framework is currently exclusively built for use in developing
apps. It is not yet suitable for production usage.

## Kick the tyres

0. Checkout this repo.
1. `cd` to the repo root and run the following commands:

    ```sh
    cp example/config.jsonnet .
    docker build -tenvelope-dev .

    # Run each line below in a separate shell.
    docker run -it --rm -v `pwd`:/work -p 9999:80 envelope-dev
    example/app/run
    example/foo/run
    example/bar/run
    ```

2. Open <http://localhost:9999/ingress/0/> in your browser
3. Edit config.jsonnet (your copy, not the one in the example directory) switch
   foo and bar's ports around then save the file.
4. Reload the page.
5. For cleanup purposes, Ctrl-C won't work in the docker container. Kill it via
   docker:

    ```sh
    docker rm -f $(docker ps -q --filter ancestor=envelope-dev)
    ```

## What is going on?

The above demo illustrates the following features of the envelope:

1. All traffic is proxied into and out of the container. The app itself is only
   connected to the outside world via proxies.
2. Ingress and egress is described by a simple [Jsonnet](https://jsonnet.org/)
   definition that hides the complexities of configuring the proxy directly.
3. The envelope watches `config.jsonnet` and automatically reconfigures itself
   when the file changes.
4. In development mode, the application lives outside the envelope and can thus
   be developed in your preferred IDE. Production mode is a future feature.
5. A `wiring.env` file is automatically created in the repo root. The app can
   use this to discover how to listen for traffic coming into the envelope and
   how to reach the services it depends on.
