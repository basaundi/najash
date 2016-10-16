
function $mixin(target, bases, extra){
    bases.push(extra);
    // TODO: Correct mro
    for (var i in bases){
        var base = bases[i];
        for(var k in base){
            switch(k){
                case "__class__":
                    continue
            }
            target[k] = base[k];
        }
    }
    return target;
}

function bind(t, s){
    for(var k in s) {
        var o = s[k];
        if(!!(o && o.constructor && o.call && o.apply)){
            if(k == '__new__'){
                t[k] = s[k];
            }else{
                (function(key, v){
                    Object.defineProperty(t, k, {
                        enumerable: true,
                        get: function(){
                            if(this.__class__ === type) return v;
                            return v.bind(null, this);
                        }
                    });
                })(k, s[k]);
            }
        }else{
            t[k] = s[k];
        }
    }
}

function type(name, bases, dict){
    if(!bases.length) bases = [object];
    function class_ () {
        var args = Array.prototype.slice.call(arguments);
        args.unshift(class_);
        var x = class_.__new__.apply(class_, args);
        x.__class__ = class_;
        x.__init__.apply(this, arguments);
        return x;
    }
    class_.__name__ = name;
    class_.__class__ = type;
    var base = $mixin({}, bases, dict);
    bind(class_, base);
    return class_;
}
type.__class__ = type;

// Type system
var object = {
    __class__: type,
    __name__: 'object',
    __new__: function(cls){
        return Object.create(cls);
    },
}

var __builtins__ = {name: '__builtins__'}
function $module(name, body){
  function _import(){
    if(!body.scope){
      body.scope = Object.create(__builtins__)
      body.scope.__name__ = name
      var old_scope = $module.scope
      $module.scope = body.scope
      body.call(body.scope)
      $module.scope = old_scope
    }
    return body.scope
  }
  $module.modules[name] = _import;
}
$module.modules = {}
$module.scope = null

function $def(func){
  $module.scope[func.name] = func
}

function $class(bases, body){
  var name = body.name
  body.scope = {}

  var old_scope = $module.scope
  $module.scope = body.scope
  body.call(body.scope)
  $module.scope = old_scope

  cls = type(name, bases, body.scope)
  $module.scope[name] = cls
  return cls
}

function $import(module, name, asname){
  var ret = $module.modules[module]()
  var alias = module
  if(name){
    ret = ret[name]
    alias = name
  }
  if(asname){
    alias = asname
  }
  if($module.scope)
      $module.scope[alias] = ret
  return ret
}


function builtins(){
$module.scope = this.scope = __builtins__

$def(Math.abs)
$def(type)
$def(Math.pow)

$def(function print(){
  for(var arg in arguments)
    console.log(arguments[arg])
})

$def(function* enumerate(iterable, start){
  start = start || 0;
  for(var el of iterable) yield [start++, el]
})

}; builtins.call(builtins)