from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "DATE_TRUNC('second', CURRENT_TIMESTAMP)"


@compiles(utcnow, 'mssql')
def ms_utcnow(element, compiler, **kw):
    return "GETUTCDATE()"
