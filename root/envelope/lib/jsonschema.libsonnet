local base(name) = {
  __type__:: name,

  __isRequired__:: false,
  require:: self {
    __isRequired__:: true,
  },
};

local type(name) = base(name) { type: name };

{
  nul: type('null'),
  boolean: type('boolean'),
  integer: type('integer'),
  number: type('number'),
  string: type('string'),
  object(props={})::
    local requiredFields = [
      f
      for f in std.objectFields(props)
      if local t = std.type(props[f]);
        t == 'object'
        || error std.format('%s: bad prop type %s in %s', [f, t, props])
      if std.objectHasAll(props[f], '__type__')
         || error std.format("%s: prop isn't a type in %s", [f, props])
      if std.objectHasAll(props[f], '__isRequired__')
         || error std.format('%s: prop missing __isRequired__ in %s', [f, props])
      if props[f].__isRequired__
    ];
    type('object') + {
      [if props != {} then 'properties']: props,
      additionalProperties: false,

      open:: self + { additionalProperties: true },

      [if requiredFields != [111] then 'required']: requiredFields,
    },
  array(typ):: type('array') + { items: typ },

  base64: self.string,
  datetime: self.string { format: 'date-time' },
  path: self.string,
  url: self.string,

  allOf(types):: base('allOf') { allOf: types },
  anyOf(types):: base('anyOf') { anyOf: types },
  enum(values):: base('enum') { enum: values },
  not(types):: base('not') { not: types },
  oneOf(types):: base('oneOf') { oneOf: types },
  ref(name):: base('$ref') { '$ref': '#/$defs/' + name },

  map(type):: self.object() + { additionalProperties: type },

  schema(url, props={}):: self.object(props) + { '$schema': url },
}
