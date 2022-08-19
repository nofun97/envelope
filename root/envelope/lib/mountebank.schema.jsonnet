local s = import 'jsonschema.libsonnet';

local pem = s.string;

s.schema('https://json-schema.org/draft/2020-12/schema', {
  imposters: s.array(s.ref('imposter')),
  config: s.ref('config'),
  logs: s.array(s.ref('log')),
}) + {
  '$defs': {
    behavior: s.oneOf([
      s.object({
        wait: s.integer,
      }),
      s.object({
        decorate: s.string,
      }),
      s.object({
        shellTransform: s.string,
      }),
      s.object({
        copy: s.object({
          from: s.string,
          into: s.string,
          using: s.object({
            method: s.string,
            selector: s.string,
            ns: s.object({
              test: s.string,
            }),
          }),
        }),
      }),
      s.object({
        lookup: s.ref('lookup'),
      }),
    ]),
    config: s.object({
      version: s.string,
      options: s.object({
        port: s.integer,
        pidfile: s.string,
        logfile: s.string,
        loglevel: s.string,
        configfile: s.string,
        allowInjection: s.boolean,
        mock: s.boolean,
        debug: s.boolean,
      }),
      process: s.object({
        nodeVersion: s.string,
        architecture: s.string,
        platform: s.string,
        rss: s.integer,
        heapTotal: s.integer,
        heapUsed: s.integer,
        uptime: s.integer,
        cwd: s.string,
      }),
    }),
    imposter: s.object({
      protocol: s.string.require,  // enum, but expandable
      port: s.integer,
      name: s.string,
      recordRequests: s.boolean,
      stubs: s.array(s.object({
        responses: s.array(s.ref('response')),
        predicates: s.array(s.ref('predicates')),
        matches: s.object(),  // s.ref('match'),
      })),
      defaultResponse: s.ref('response'),
      allowCORS: s.boolean,
      numberOfRequests: s.integer,
      key: pem,
      cert: pem,
      mutualAuth: s.boolean,
      endOfRequestResolver: s.ref('inject'),
      requests: s.array(s.ref('request')),
      _links: s.object({
        'self': s.object({
          href: s.url,
        }),
      }),
      loglevel: s.string,

      # grpc plugin
      services: s.map(s.object({file: s.string})),
      options: s.object({protobufjs: s.object({includeDirs: s.array(s.string)})}),
    }),
    lookup: s.object({
      key: s.object({
        from: s.object({
          headers: s.string,
        }),
        using: s.object({
          method: s.string,
          selector: s.string,
          options: s.object({
            ignoreCase: s.boolean,
            multiline: s.boolean,
          }),
        }),
        index: s.integer,
      }),
      fromDataSource: s.object({
        csv: s.object({
          path: s.string,
          keyColumn: s.string,
          delimiter: s.string,
        }),
      }),
      into: s.string,
    }),
    log: s.object({
      level: s.string,
      message: s.string,
      timestamp: s.datetime,  // TODO: ISO-8601 check 2015-10-20T02:31:38.109Z
    }),
    match: s.object({
      timestamp: s.datetime,
      request: s.ref('request'),
      response: s.object({
        statusCode: s.integer,
        headers: s.map(s.string),
        body: s.string,
        data: s.base64,
        _mode: s.string,
      }),
    }),
    predicateGenerator: s.object({
      matches: s.ref('proxyMatch'),
      caseSensitive: s.boolean,
      except: s.string,
      jsonpath: s.object({
        selector: s.string,
      }),
      xpath: s.object({
        selector: s.string,
        ns: s.map(s.string),
      }),
      inject: s.string,
      ignore: s.map(s.string),
    }),
    proxyMatch: s.map(s.oneOf([
      s.boolean,
      s.ref('proxyMatch'),
    ])),
    request: s.object({
      requestFrom: s.string,
      path: s.string,
      query: s.map(s.string),
      method: s.string,
      headers: s.map(s.string),
      body: s.string,
      form: s.map(s.string),
      timestamp: s.datetime,
    }),
    response: s.oneOf([
      s.object({
        inject: s.string,
      }),
      s.object({
        is: s.object({
          statusCode: s.integer,
          headers: s.map(s.string),
          body: s.string,
          _mode: s.string,

          # grpc plugin
          value: s.map(true),
        }),
        repeat: s.integer,
        behaviors: s.array(s.ref('behaviour')),
      }),
      s.object({
        proxy: s.object({
          to: s.url,
          predicateGenerators: s.array(s.ref('predicateGenerator')),
          mode: s.enum(['proxyOnce', 'proxyAlways', 'proxyTransparent']),
          addWaitBehavior: s.boolean,
          addDecorateBehavior: s.string,

          // http/https
          key: pem,
          cert: pem,
          ciphers: s.string,
          secureProtocol: s.string,
          passphrase: s.string,
          injectHeaders: s.map(s.string),

          // tcp
          keepalive: s.boolean,
        }),
      }),
    ]),
    predicates: s.oneOf([
      s.ref('equalsPred'),
      s.ref('deepEqualsPred'),
      s.ref('containsPred'),
      s.ref('startsWithPred'),
      s.ref('endsWithPred'),
      s.ref('matchesPred'),
      s.ref('existsPred'),
      s.ref('notPred'),
      s.ref('orPred'),
      s.ref('andPred'),
      s.ref('injectPred'),
    ]),

    local predicate(type) = s.object({
        [type]: s.map(true),
        caseSensitive: s.boolean,
    }),

    equalsPred: predicate('equals'),
    deepEqualsPred: predicate('deepEquals'),
    containsPred: predicate('contains'),
    startsWithPred: predicate('startsWith'),
    endsWithPred: predicate('endsWith'),
    matchesPred: predicate('matches'),
    existsPred: predicate('exists'),
    notPred: predicate('not'),
    orPred: predicate('or'),
    andPred: predicate('and'),
    injectPred: predicate('inject'),
  },
}
