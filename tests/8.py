try:
    operation_that_can_throw_ioerror()
except IOError:
    handle_the_exception_somehow()
else:
     # we don't want to catch the IOError if it's raised
    another_operation_that_can_throw_ioerror()
finally:
    something_we_always_need_to_do()

